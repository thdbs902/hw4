// Lets any page ask DD a question: opens the chat widget and sends the message.
const EVENT = 'cc:ask-dd'

export const askDD = (message: string) => window.dispatchEvent(new CustomEvent(EVENT, { detail: message }))

export function onAskDD(handler: (message: string) => void) {
  const listener = (e: Event) => handler((e as CustomEvent<string>).detail)
  window.addEventListener(EVENT, listener)
  return () => window.removeEventListener(EVENT, listener)
}
