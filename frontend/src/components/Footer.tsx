import { Link } from 'react-router-dom'

const YEAR = new Date().getFullYear()

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div>
          <p className="footer-brand">Campus Customs</p>
          <p>57 Broadway, New Haven, CT 06511</p>
        </div>
        <div className="footer-links">
          <Link to="/products">Shop</Link>
          <Link to="/about">About Us</Link>
          <Link to="/login">Log in</Link>
        </div>
      </div>
      <p className="footer-fine">© {YEAR} Campus Customs · Class project demo</p>
    </footer>
  )
}
