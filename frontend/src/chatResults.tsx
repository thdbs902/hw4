import { createContext, useContext, useState, type ReactNode } from 'react'
import type { Product } from './api'

// Product matches from the latest DD reply, shared between the chat widget (writes)
// and the results panel on the page (reads).
export interface ChatResults {
  title: string
  products: Product[]
  totalMatches: number | null
  question: string
  // Bumped on every new result so the panel can scroll itself into view.
  version: number
  // Page the shopper was on when DD answered (results stay expanded there).
  fromPath: string
}

interface ChatResultsState {
  results: ChatResults | null
  show: (r: Omit<ChatResults, 'version' | 'fromPath'>) => void
  clear: () => void
}

const ChatResultsContext = createContext<ChatResultsState | null>(null)

export function ChatResultsProvider({ children }: { children: ReactNode }) {
  const [results, setResults] = useState<ChatResults | null>(null)

  const value: ChatResultsState = {
    results,
    show: (r) =>
      setResults((prev) => ({ ...r, version: (prev?.version ?? 0) + 1, fromPath: window.location.pathname })),
    clear: () => setResults(null),
  }
  return <ChatResultsContext.Provider value={value}>{children}</ChatResultsContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useChatResults() {
  const ctx = useContext(ChatResultsContext)
  if (!ctx) throw new Error('useChatResults must be used inside <ChatResultsProvider>')
  return ctx
}
