import { useState } from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'
import { setSoundOn, soundOn, startCrowd, stopCrowd } from '../sound'

const links = [
  { to: '/', label: 'Home', end: true },
  { to: '/products', label: 'Products' },
  { to: '/about', label: 'About Us' },
]

export default function NavBar() {
  const [open, setOpen] = useState(false)
  const close = () => setOpen(false)
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [sound, setSound] = useState(soundOn)

  return (
    <header className="nav">
      <div className="nav-strip">🏈 The Halftime Collection · Officially licensed Yale merch · 57 Broadway</div>
      <nav className="nav-bar">
        <Link to="/" className="brand" onClick={close}>
          <img className="brand-shield" src="/media/brand/yale-shield.svg" alt="" />
          <span className="brand-name">Campus Customs</span>
        </Link>
        <button
          className="nav-toggle"
          aria-label="Toggle menu"
          aria-expanded={open}
          onClick={() => setOpen((o) => !o)}
        >
          ☰
        </button>
        <button
          type="button"
          className="sound-toggle"
          aria-label={sound ? 'Mute click sounds' : 'Turn click sounds on'}
          aria-pressed={sound}
          onClick={() => {
            setSoundOn(!sound)
            setSound(!sound)
            if (sound) stopCrowd()
            else startCrowd()
          }}
        >
          {sound ? '🔊' : '🔇'}
        </button>
        <ul className={`nav-links ${open ? 'open' : ''}`}>
          {links.map((l) => (
            <li key={l.to}>
              <NavLink to={l.to} end={l.end} onClick={close}>
                {l.label}
              </NavLink>
            </li>
          ))}
          {user ? (
            <>
              <li>
                <NavLink to="/account" className="nav-cta" onClick={close}>
                  Hi, {user.first_name}
                </NavLink>
              </li>
              <li>
                <button
                  type="button"
                  className="nav-logout"
                  onClick={async () => {
                    close()
                    await logout()
                    navigate('/')
                  }}
                >
                  Log out
                </button>
              </li>
            </>
          ) : (
            <>
              <li>
                <NavLink to="/login" onClick={close}>
                  Log in
                </NavLink>
              </li>
              <li>
                <NavLink to="/create-account" className="nav-cta" onClick={close}>
                  Create account
                </NavLink>
              </li>
            </>
          )}
        </ul>
      </nav>
    </header>
  )
}
