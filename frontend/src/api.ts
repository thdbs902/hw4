// Types + calls to the FastAPI backend (proxied by Vite to http://127.0.0.1:8000).

export interface SizeStock {
  size: string
  quantity: number
}

// Same shape as the product cards saved in chat_messages.products_json.
export interface Product {
  product_id: string
  name: string
  garment_type: string
  description: string
  colors: string[]
  search_tags: string[]
  image_file_path: string
  image_url: string
  price: number
  inventory: SizeStock[]
  total_stock: number
}

// products are structured matches from the agent, rebuilt from the database by the backend.
export interface ChatReply {
  reply: string
  products: Product[]
  results_title: string
  total_matches: number | null
  blocked?: boolean
}

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json() as Promise<T>
}

// FastAPI errors come back as { detail: string } or { detail: [{ msg }] } for validation.
async function postJson<T>(url: string, body?: unknown): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => null)
    const detail = data?.detail
    const message = Array.isArray(detail)
      ? detail.map((d: { msg: string }) => d.msg.replace(/^Value error, /, '')).join(' ')
      : detail
    throw new Error(message || `${res.status} ${res.statusText}`)
  }
  return (res.status === 204 ? undefined : res.json()) as Promise<T>
}

// ---------- accounts ----------

export interface User {
  id: number
  first_name: string
  last_name: string
  name: string
  email: string
}

export interface RegisterInput {
  first_name: string
  last_name: string
  email: string
  password: string
  confirm_password: string
}

export const fetchMe = () => getJson<User | null>('/api/auth/me')
export const login = (email: string, password: string) =>
  postJson<User>('/api/auth/login', { email, password })
export const register = (input: RegisterInput) => postJson<User>('/api/auth/register', input)
export const logout = () => postJson<void>('/api/auth/logout')

export const fetchProducts = () => getJson<Product[]>('/api/products')

export const fetchProduct = (id: string) =>
  getJson<Product>(`/api/products/${encodeURIComponent(id)}`)

// Bump when the served images change (e.g. clean_images.py) so browsers drop cached copies.
const IMAGE_VERSION = 'clean-5'
export const imageSrc = (p: Pick<Product, 'image_url'>) => `${p.image_url}?v=${IMAGE_VERSION}`

export const formatPrice = (price: number) => `$${price.toFixed(2)}`

// ---------- chat (DD agent) ----------

export interface ChatTurn {
  role: 'user' | 'assistant'
  content: string
}

export interface PageInfo {
  path: string
  product_id: string | null
}

/** Sends the new message, recent turns (used for guests) and the current page; the backend runs DD. */
export const sendChatMessage = (message: string, history: ChatTurn[] = [], page?: PageInfo) =>
  postJson<ChatReply>('/api/chat', { message, history: history.slice(-12), page })

export interface HistoryMessage {
  role: 'user' | 'assistant'
  content: string
  products: Product[]
  created_at: string
}

/** Saved chat for the logged-in shopper (empty for guests). */
export const fetchChatHistory = () => getJson<HistoryMessage[]>('/api/chat/history')
