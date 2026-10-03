import { useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { useChatResults } from '../chatResults'
import ProductCard from './ProductCard'

// "DD's picks": the product cards from the latest chat search, shown at the top of every page.
// Uses the same ProductCard as the Products page, so each card opens /products/:productId.
export default function ChatResultsPanel() {
  const { results, clear } = useChatResults()
  const ref = useRef<HTMLElement>(null)
  const { pathname } = useLocation()
  // On a product's own page the picks collapse to a slim bar so the product is what you see.
  const onDetailPage = pathname.startsWith('/products/')
  const [expandedOn, setExpandedOn] = useState<string | null>(null)
  const collapsed = onDetailPage && expandedOn !== pathname && results?.fromPath !== pathname

  useEffect(() => {
    if (results) ref.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [results?.version]) // eslint-disable-line react-hooks/exhaustive-deps

  if (!results || results.products.length === 0) return null
  const { title, products, totalMatches, question } = results
  const count =
    totalMatches && totalMatches > products.length
      ? `Showing ${products.length} of ${totalMatches} matches`
      : `${products.length} ${products.length === 1 ? 'item' : 'items'}`

  if (collapsed) {
    return (
      <div className="chat-results-bar">
        <button type="button" onClick={() => setExpandedOn(pathname)}>
          ↑ Back to DD's picks: {title || 'Matching items'} ({products.length})
        </button>
      </div>
    )
  }

  return (
    <section ref={ref} className="chat-results" aria-live="polite" aria-label="Products from chat">
      <div className="chat-results-inner">
        <div className="chat-results-head">
          <div>
            <p className="eyebrow dark">DD's picks · {count}</p>
            <h2>{title || 'Matching items'}</h2>
            <p className="muted">You asked: “{question}”</p>
          </div>
          <button type="button" className="btn btn-outline btn-sm" onClick={clear}>
            Clear ✕
          </button>
        </div>
        <div className="grid">
          {products.map((p) => (
            <ProductCard key={p.product_id} product={p} />
          ))}
        </div>
      </div>
    </section>
  )
}
