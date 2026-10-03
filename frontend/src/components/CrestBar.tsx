import { Link } from 'react-router-dom'

import { useState } from 'react'
import { COLLEGES, SCHOOLS, type Crest } from '../crests'

// "Shop by college & school": the real crests, cropped from CC's own product photos
// (backend/crop_crests.py -> data/brand/crests/, served at /media/brand/crests/<id>.png).
// A college/school without a crest photo falls back to a styled shield with its initials.
export function CrestImage({ crest, className = '' }: { crest: Crest; className?: string }) {
  const [missing, setMissing] = useState(false)
  if (missing) return <span className={`shield s0 ${className}`}>{crest.mono}</span>
  return (
    <img
      className={`crest-img ${className}`}
      src={`/media/brand/crests/${crest.id}.png`}
      alt={`${crest.name} crest`}
      onError={() => setMissing(true)}
    />
  )
}

export default function CrestBar() {
  return (
    <nav className="crestbar" aria-label="Shop by Yale college and school">
      <div className="crestbar-inner">
        <img className="crestbar-shield" src="/media/brand/yale-shield.svg" alt="Yale University shield" />
        <span className="crestbar-label">
          Yale <b>Colleges</b>
        </span>
        {COLLEGES.map((c) => (
          <Link key={c.id} to={`/products?q=${encodeURIComponent(c.query)}`} className="crest" title={`${c.name} College`}>
            <CrestImage crest={c} />
            <span className="crest-name">{c.name}</span>
          </Link>
        ))}
        <span className="crestbar-label">
          Yale <b>Schools</b>
        </span>
        {SCHOOLS.map((c) => (
          <Link key={c.id} to={`/products?q=${encodeURIComponent(c.query)}`} className="crest school" title={`Yale ${c.name}`}>
            <CrestImage crest={c} />
            <span className="crest-name">{c.name}</span>
          </Link>
        ))}
      </div>
    </nav>
  )
}
