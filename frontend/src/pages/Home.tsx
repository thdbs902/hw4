import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchProducts, imageSrc, type Product } from '../api'
import ProductCard from '../components/ProductCard'
import { CrestImage } from '../components/CrestBar'
import { COLLEGES, SCHOOLS } from '../crests'
import HandsomeDan from '../components/HandsomeDan'

const FEATURED_IDS = [
  'basic-hoodie-big-yale',
  '2025-yale-vs-harvard-t-shirt',
  'baseball-left-chest-crewneck',
  'benjamin-franklin-fleece-jacket',
]

const CATEGORIES = ['Hoodies', 'Crewnecks', 'Quarter-zips', 'T-shirts', 'Jackets', 'College', 'Dad', 'Mom', 'Football', 'Baseball']

export default function Home() {
  const [featured, setFeatured] = useState<Product[]>([])

  useEffect(() => {
    fetchProducts()
      .then((all) => {
        const picks = FEATURED_IDS.map((id) => all.find((p) => p.product_id === id)).filter(
          (p): p is Product => Boolean(p),
        )
        setFeatured(picks.length ? picks : all.slice(0, 4))
      })
      .catch(() => setFeatured([]))
  }, [])

  return (
    <>
      <section className="hero hero-split">
        <div className="hero-inner">
          <div className="scoreboard" aria-label="Halftime: Yale vs Harvard">
            <span className="team">YALE</span>
            <span className="score">21</span>
            <span className="clock">
              HALFTIME<b>15:00</b>
            </span>
            <span className="score">17</span>
            <span className="team">HARVARD</span>
          </div>
          <p className="eyebrow">The Halftime Collection · Live from Broadway</p>
          <h1>
            Wear the blue.
            <br />
            <em>Own the room.</em>
          </h1>
          <p className="hero-copy">
            Campus Customs is where Yale spirit gets dressed up. Hoodies for late nights in the
            library, crewnecks for game day, and residential college gear you'll keep long after
            graduation.
          </p>
          <div className="hero-actions">
            <Link to="/products" className="btn btn-gold">
              Shop the collection
            </Link>
            <Link to="/about" className="btn btn-ghost">
              Our story
            </Link>
          </div>
        </div>
        <div className="beams" aria-hidden="true">
          <i />
          <i />
          <i />
        </div>
        <HandsomeDan />
        <div className="hero-stage" aria-hidden="true">
          {featured.slice(0, 3).map((p, i) => (
            <Link key={p.product_id} to={`/products/${p.product_id}`} className={`float-card f${i}`} tabIndex={-1}>
              <img src={imageSrc(p)} alt="" />
              <span className="tag-price">${p.price.toFixed(0)}</span>
            </Link>
          ))}
        </div>
      </section>

      <nav className="ticker" aria-label="Shop by category">
        <div className="ticker-track">
          {[0, 1].map((copy) =>
            CATEGORIES.map((c) => (
              <Link key={`${copy}-${c}`} to={`/products?q=${encodeURIComponent(c)}`} tabIndex={copy ? -1 : 0}>
                {c} <span>★</span>
              </Link>
            )),
          )}
        </div>
      </nav>

      <section className="crest-wall" aria-label="Shop by Yale college and school">
        <div className="crest-wall-head">
          <img src="/media/brand/yale-shield.svg" alt="Yale University shield" />
          <div>
            <p className="eyebrow dark">The official Yale store on Broadway</p>
            <h2>Rep your college. Rep your school.</h2>
          </div>
        </div>
        {[
          ['Residential Colleges', COLLEGES],
          ['Professional Schools', SCHOOLS],
        ].map(([label, list]) => (
          <div key={label as string}>
            <h4>{label as string}</h4>
            <div className="crest-grid">
              {(list as typeof COLLEGES).map((c) => (
                <Link key={c.id} to={`/products?q=${encodeURIComponent(c.query)}`} className="crest-tile">
                  <CrestImage crest={c} />
                  <span>{c.name}</span>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </section>

      <section className="pillars">
        <div>
          <h3>Officially licensed</h3>
          <p>Every piece carries real Yale marks, so the bulldog on your chest is the real deal.</p>
        </div>
        <div>
          <h3>Made for every college</h3>
          <p>From Berkeley to Branford, rep your residential college as loudly as you like.</p>
        </div>
        <div>
          <h3>Honest answers</h3>
          <p>Ask DD, our chat assistant, about sizes and stock. No guessing, just what's on the shelf.</p>
        </div>
      </section>

      <section className="section">
        <div className="section-head">
          <h2>Fan favourites</h2>
          <Link to="/products" className="link-arrow">
            See everything →
          </Link>
        </div>
        <div className="grid">
          {featured.map((p) => (
            <ProductCard key={p.product_id} product={p} />
          ))}
        </div>
      </section>
    </>
  )
}
