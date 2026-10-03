import { Link } from 'react-router-dom'

export default function About() {
  return (
    <>
      <section className="hero hero-short">
        <div className="hero-inner">
          <p className="eyebrow">About Us</p>
          <h1>
            Blue is not a colour here.
            <br />
            <em>It's a feeling.</em>
          </h1>
        </div>
      </section>

      <section className="section prose">
        <h2>Who we are</h2>
        <p>
          Campus Customs is a Yale merch shop on Broadway in New Haven, right where campus spills
          into the city. We started with a simple idea: the clothes you wear around Yale should feel
          as good as the memories you make here.
        </p>
        <p>
          We carry officially licensed Yale apparel: hoodies, crewnecks, quarter-zips, tees and
          jackets, plus gear for every residential college. Whether you're a first-year
          finding your people, a parent visiting for the weekend, or an alum who still owns a
          sweatshirt from move-in day, we've got something with your name on it (figuratively).
        </p>

        <h2>What we care about</h2>
        <ul>
          <li>
            <strong>Real Yale, real quality.</strong> Licensed designs on pieces built to survive
            dining halls, finals, and a few too many washes.
          </li>
          <li>
            <strong>Every college gets a spotlight.</strong> Your residential college is your home
            on campus, so we make sure it gets its own gear.
          </li>
          <li>
            <strong>Straight talk.</strong> Our assistant DD tells you the real price and what's
            actually in stock in your size, so you never fall for something we don't have.
          </li>
        </ul>

        <h2>Come say hi</h2>
        <p>
          Find us at <strong>57 Broadway, New Haven, CT 06511</strong>, or shop online any time.
        </p>
        <Link to="/products" className="btn btn-navy">
          Browse the collection
        </Link>
      </section>
    </>
  )
}
