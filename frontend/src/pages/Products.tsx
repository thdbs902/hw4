import { useEffect, useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { fetchProducts, type Product } from '../api'
import ProductCard from '../components/ProductCard'

export default function Products() {
  const [products, setProducts] = useState<Product[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [params] = useSearchParams()
  const [query, setQuery] = useState(params.get('q') ?? '')

  useEffect(() => {
    fetchProducts()
      .then(setProducts)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const visible = useMemo(() => {
    // Every word must match; a trailing "s" is optional, so "Hoodies" finds "hoodie".
    const phrase = query.trim().toLowerCase()
    const words = phrase.split(/\s+/).filter(Boolean)
    if (!words.length) return products
    const textOf = (p: Product) =>
      [p.name, p.garment_type, p.description, ...p.colors, ...p.search_tags].join(' ').toLowerCase()
    // An exact phrase ("school of art") wins when it exists, so "art" doesn't match "quarter-zip".
    const exact = products.filter((p) => textOf(p).includes(phrase))
    if (words.length > 1 && exact.length) return exact
    return products.filter((p) => {
      const text = textOf(p)
      return words.every((w) => text.includes(w) || text.includes(w.replace(/s$/, '')))
    })
  }, [products, query])

  return (
    <section className="section">
      <div className="page-head">
        <p className="eyebrow dark">The collection</p>
        <h1>Products</h1>
        <input
          className="search"
          type="search"
          placeholder="Search hoodies, colleges, colours…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        {!loading && !error && (
          <p className="muted">
            {visible.length} of {products.length} items
          </p>
        )}
      </div>

      {loading && <p className="muted">Loading the collection…</p>}
      {error && <p className="error">Could not load products ({error}). Is the backend running?</p>}

      <div className="grid">
        {visible.map((p) => (
          <ProductCard key={p.product_id} product={p} />
        ))}
      </div>
    </section>
  )
}
