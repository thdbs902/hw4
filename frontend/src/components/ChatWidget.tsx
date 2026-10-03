import { useEffect, useRef, useState, type FormEvent } from 'react'
import { useLocation } from 'react-router-dom'
import { fetchChatHistory, sendChatMessage, type Product } from '../api'
import { useAuth } from '../auth'
import { useChatResults } from '../chatResults'
import DDAvatar from './DDAvatar'
import { onAskDD } from '../askDD'

interface Message {
  role: 'user' | 'assistant'
  content: string
  // Turn rejected by the provider's safety filter; never re-sent as history.
  blocked?: boolean
  // Product cards this reply put on the page (also restored from saved history).
  products?: Product[]
  question?: string
}

const greeting: Message = {
  role: 'assistant',
  content: "Hi! I'm DD, the Campus Customs merch assistant. Ask me about hoodies, sizes, or prices.",
}

const greetingFor = (firstName: string): Message => ({
  role: 'assistant',
  content: `Welcome back, ${firstName}! I'm DD. Ask me about hoodies, sizes, or prices.`,
})

export default function ChatWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([greeting])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)
  const chatResults = useChatResults()
  const { user, loading: authLoading } = useAuth()
  const { pathname } = useLocation()
  const productId = pathname.match(/^\/products\/([^/]+)$/)?.[1] ?? null
  const [loadedFor, setLoadedFor] = useState<number | null | undefined>(undefined)

  // Logged in: show the saved conversation from chat_messages. Logged out / guest: start fresh.
  const userId = authLoading ? undefined : (user?.id ?? null)
  if (userId !== undefined && userId !== loadedFor) {
    setLoadedFor(userId)
    setMessages([user ? greetingFor(user.first_name) : greeting])
    if (user) {
      fetchChatHistory()
        .then((saved) => {
          const restored: Message[] = []
          saved.forEach((m, i) =>
            restored.push({
              role: m.role,
              content: m.content,
              products: m.products,
              question: m.role === 'assistant' ? saved[i - 1]?.content : undefined,
            }),
          )
          setMessages([greetingFor(user.first_name), ...restored])
        })
        .catch(() => {})
    }
  }

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, open])

  // "Ask DD about this" buttons elsewhere on the site open the chat and send their question.
  const sendRef = useRef<(text: string) => void>(() => {})
  useEffect(() => onAskDD((text) => sendRef.current(text)), [])

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    send(input.trim())
  }

  async function send(text: string) {
    if (!text || sending) return
    // History sent to the agent excludes greetings and blocked turns (used for guests only;
    // for logged-in shoppers the backend reads chat_messages instead).
    const history = messages
      .filter((m, i) => i > 0 && !m.blocked)
      .map(({ role, content }) => ({ role, content }))
    setMessages((m) => [...m, { role: 'user', content: text }])
    setInput('')
    setSending(true)
    try {
      const { reply, blocked, products, results_title, total_matches } = await sendChatMessage(text, history, {
        path: pathname,
        product_id: productId,
      })
      if (products.length > 0) {
        chatResults.show({ title: results_title, products, totalMatches: total_matches, question: text })
      }
      setMessages((m) => {
        const next = [...m]
        if (blocked) next[next.length - 1] = { ...next[next.length - 1], blocked: true }
        return [...next, { role: 'assistant', content: reply, blocked, products, question: text }]
      })
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: (err as Error).message || 'Sorry, I could not reach the shop right now.' },
      ])
    } finally {
      setSending(false)
    }
  }

  // Keep the latest send() for "Ask DD about this" events.
  useEffect(() => {
    sendRef.current = (text: string) => {
      setOpen(true)
      send(text)
    }
  })

  return (
    <div className="chat">
      {open && (
        <section className="chat-panel" aria-label="Chat with DD">
          <header className="chat-head">
            <DDAvatar size={46} />
            <div className="chat-head-text">
              <p className="chat-title">Ask DD</p>
              <p className="chat-sub">
                <span className="online-dot" /> CC's bulldog stylist · real prices &amp; stock
              </p>
            </div>
            <button className="chat-close" aria-label="Close chat" onClick={() => setOpen(false)}>
              ×
            </button>
          </header>
          <div className="chat-log">
            {messages.map((m, i) => (
              <div key={i} className={`bubble ${m.role}`}>
                {m.content}
                {!!m.products?.length && (
                  <button
                    type="button"
                    className="bubble-note"
                    onClick={() =>
                      chatResults.show({
                        title: 'From your chat',
                        products: m.products!,
                        totalMatches: null,
                        question: m.question ?? '',
                      })
                    }
                  >
                    ↖ {m.products.length} {m.products.length === 1 ? 'item' : 'items'}: show on the page
                  </button>
                )}
              </div>
            ))}
            {sending && (
              <div className="bubble assistant typing" aria-label="DD is typing">
                <span className="dots">
                  <i />
                  <i />
                  <i />
                </span>
              </div>
            )}
            <div ref={endRef} />
          </div>
          <form className="chat-form" onSubmit={handleSubmit}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Do you have a navy hoodie in M?"
              aria-label="Message"
            />
            <button type="submit" disabled={sending || !input.trim()}>
              Send
            </button>
          </form>
        </section>
      )}
      <button
        className="chat-launcher"
        aria-label={open ? 'Close chat' : 'Open chat'}
        onClick={() => setOpen((o) => !o)}
      >
        {open ? (
          '×'
        ) : (
          <>
            <DDAvatar size={34} />
            <span>Ask DD</span>
          </>
        )}
      </button>
    </div>
  )
}
