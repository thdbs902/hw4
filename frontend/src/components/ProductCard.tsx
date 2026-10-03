import { Link } from 'react-router-dom'
import { formatPrice, imageSrc, type Product } from '../api'
import { swatchFor } from '../colors'

function shortDescription(text: string, max = 110) {
  if (text.length <= max) return text
  return text.slice(0, text.lastIndexOf(' ', max)) + '…'
}

// Problem 9: stock badge from the real inventory rows on the card.
function stockBadge(p: Product): { text: string; tone: 'ok' | 'low' | 'out' } {
  const out = p.inventory.filter((s) => s.quantity === 0).map((s) => s.size)
  const low = p.inventory.filter((s) => s.quantity > 0 && s.quantity <= 3)
  if (p.total_stock === 0) return { text: 'Sold out', tone: 'out' }
  if (low.length) return { text: `Only ${low[0].quantity} left in ${low[0].size}`, tone: 'low' }
  if (out.length) return { text: `Sold out in ${out.join(', ')}`, tone: 'out' }
  return { text: 'In stock · all sizes', tone: 'ok' }
}

export default function ProductCard({ product }: { product: Product }) {
  const badge = stockBadge(product)
  return (
    <Link to={`/products/${product.product_id}`} className="card" aria-label={`View details for ${product.name}`}>
      <div className="card-img">
        <img src={imageSrc(product)} alt={product.name} loading="lazy" />
        <span className={`stock-badge ${badge.tone}`}>{badge.text}</span>
      </div>
      <div className="card-body">
        <h3 className="card-name">{product.name}</h3>
        <p className="card-price">{formatPrice(product.price)}</p>
        <p className="card-desc">{shortDescription(product.description)}</p>
        <div className="card-foot">
          <span className="card-swatches" aria-label={`${product.colors.length} colours`}>
            {product.colors.map((c) => (
              <span key={c} className="dot" style={{ background: swatchFor(c) }} title={c} />
            ))}
          </span>
          <span className="card-cta">View details →</span>
        </div>
      </div>
    </Link>
  )
}
