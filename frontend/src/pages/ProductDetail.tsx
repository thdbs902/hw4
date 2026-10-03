import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchProduct, formatPrice, imageSrc, type Product } from '../api'
import { swatchFor } from '../colors'
import { askDD } from '../askDD'

function stockLabel(qty: number) {
  if (qty === 0) return 'Sold out'
  if (qty <= 3) return `Only ${qty} left`
  return `${qty} in stock`
}

export default function ProductDetail() {
  const { productId = '' } = useParams()
  // Result is tagged with the id it belongs to, so a stale result reads as "loading".
  const [result, setResult] = useState<{ id: string; product?: Product; error?: string }>()

  useEffect(() => {
    fetchProduct(productId)
      .then((product) => setResult({ id: productId, product }))
      .catch((e: Error) => setResult({ id: productId, error: e.message }))
  }, [productId])

  const current = result?.id === productId ? result : undefined
  const product = current?.product
  const error = current?.error

  if (error) {
    return (
      <section className="section">
        <p className="error">We couldn't find that product ({error}).</p>
        <Link to="/products" className="link-arrow">
          ← Back to products
        </Link>
      </section>
    )
  }
  if (!product) return <section className="section muted">Loading…</section>

  // key resets colour/size choices when moving to another product
  return <ProductView key={product.product_id} product={product} />
}

function ProductView({ product }: { product: Product }) {
  const [color, setColor] = useState(product.colors[0] ?? '')
  const [size, setSize] = useState<string | null>(null)

  const chosen = product.inventory.find((s) => s.size === size)
  const availableSizes = product.inventory.filter((s) => s.quantity > 0).map((s) => s.size)

  return (
    <section className="section">
      <nav className="crumbs" aria-label="Breadcrumb">
        <Link to="/">Home</Link> / <Link to="/products">Products</Link> / <span>{product.name}</span>
      </nav>

      <div className="detail">
        <div className="detail-img">
          <img src={imageSrc(product)} alt={product.name} />
        </div>

        <div className="detail-info">
          <p className="eyebrow dark">{product.garment_type}</p>
          <h1>{product.name}</h1>
          <p className="detail-price">{formatPrice(product.price)}</p>
          <p className="detail-desc">{product.description}</p>

          <h4>
            Colour: <span className="picked">{color}</span>
          </h4>
          <div className="swatches" role="radiogroup" aria-label="Colour">
            {product.colors.map((c) => (
              <button
                key={c}
                type="button"
                role="radio"
                aria-checked={c === color}
                className={`swatch ${c === color ? 'selected' : ''}`}
                onClick={() => setColor(c)}
              >
                <span className="dot" style={{ background: swatchFor(c) }} />
                {c}
              </button>
            ))}
          </div>

          {product.inventory.length > 0 && (
            <>
              <h4>
                Size: <span className="picked">{size ?? 'choose a size'}</span>
              </h4>
              <div className="sizes" role="radiogroup" aria-label="Size">
                {product.inventory.map((s) => (
                  <button
                    key={s.size}
                    type="button"
                    role="radio"
                    aria-checked={s.size === size}
                    disabled={s.quantity === 0}
                    className={`size ${s.quantity === 0 ? 'out' : ''} ${s.size === size ? 'selected' : ''}`}
                    onClick={() => setSize(s.size)}
                  >
                    <span className="size-name">{s.size}</span>
                    <span className="size-qty">{stockLabel(s.quantity)}</span>
                  </button>
                ))}
              </div>
              <p className={`selection ${chosen ? 'ready' : ''}`}>
                {chosen ? (
                  <>
                    <span className="cap">{color}</span> · {chosen.size} · {formatPrice(product.price)} ·{' '}
                    {stockLabel(chosen.quantity)}
                  </>
                ) : (
                  'Pick a size to check stock.'
                )}
              </p>
            </>
          )}

          <div className="ask-dd">
            <p className="ask-dd-title">Ask DD about this</p>
            <div className="ask-dd-chips">
              <button type="button" onClick={() => askDD(`Is this in ${size ?? 'M'}?`)}>
                Is this in {size ?? 'M'}?
              </button>
              <button type="button" onClick={() => askDD('What else is like this?')}>
                What else is like this?
              </button>
              <button type="button" onClick={() => askDD(`Tell me about the ${color} one`)}>
                Tell me about the {color} one
              </button>
            </div>
          </div>

          <h4>Product details</h4>
          <dl className="specs">
            <dt>Type</dt>
            <dd className="cap">{product.garment_type}</dd>
            <dt>Colours</dt>
            <dd className="cap">{product.colors.join(', ')}</dd>
            <dt>Sizes in stock</dt>
            <dd>{availableSizes.length ? availableSizes.join(', ') : 'Currently sold out'}</dd>
            <dt>Total stock</dt>
            <dd>{product.total_stock} across all sizes</dd>
            <dt>Product ID</dt>
            <dd>{product.product_id}</dd>
          </dl>
          <div className="chips tags">
            {product.search_tags.map((t) => (
              <span key={t} className="chip">
                #{t}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
