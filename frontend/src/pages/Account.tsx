import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

export default function Account() {
  const { user, loading, logout } = useAuth()
  const navigate = useNavigate()
  const welcome = (useLocation().state as { welcome?: boolean } | null)?.welcome

  if (loading) return <section className="section muted">Loading…</section>
  if (!user) return <Navigate to="/login" replace />

  return (
    <section className="section auth">
      <div className="auth-card">
        <p className="eyebrow dark">{welcome ? 'Account created' : 'Signed in'}</p>
        <h1>Hi, {user.first_name}!</h1>
        <p className="muted">
          {welcome
            ? 'Welcome to Campus Customs. Your account is ready.'
            : "You're logged in. DD will remember your chats."}
        </p>
        <dl className="specs">
          <dt>Name</dt>
          <dd>
            {user.first_name} {user.last_name}
          </dd>
          <dt>Email</dt>
          <dd>{user.email}</dd>
        </dl>
        <Link to="/products" className="btn btn-gold">
          Start shopping
        </Link>
        <button
          type="button"
          className="btn btn-outline"
          onClick={async () => {
            await logout()
            navigate('/')
          }}
        >
          Log out
        </button>
      </div>
    </section>
  )
}
