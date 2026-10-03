# CC Usability Improvements (Problem 9)

I reviewed the site and listed 3 front-end and 3 agent/backend options, chose **2 of each**, and built them. Screenshots of the built features are in `output/app_check.html` (checks 3–5).

## Options considered

### Front end

| Option | What it adds | Why it helps a CC shopper or the business | Chosen |
|---|---|---|---|
| Filter & sort on Products | Type, colour, max price, "in stock in my size" filters + price sort | Find the right item among 102 in seconds | |
| **"Ask DD about this" button** | Chips on every product page ("Is this in M?", "What else is like this?", "Tell me about the navy one") that open the chat and send the question | Connects browsing to chat: stock answers in one tap, fewer abandoned product pages | ✅ |
| **Stock badges on cards** | "Only 2 left in L", "Sold out in XS, XL", "In stock · all sizes" on every product card | Availability visible before clicking; honest low-stock signals create urgency | ✅ |

### Agent / backend

| Option | What it adds | Why it helps | Chosen |
|---|---|---|---|
| **Find-alternatives tool** | When a size is sold out, DD finds similar same-type items that ARE in stock in that size | Turns a "sold out" dead end into a sale | ✅ |
| **Remember shopper's size** | DD saves a logged-in shopper's usual size and favourite colours and uses them next time | Personal service, fewer repeated questions | ✅ |
| Unmet-demand log | Records requests CC can't fill (pink, caps, sold-out sizes) + a report | Tells the business what to stock next | |

## What was built

| Improvement | Files | How it works | Test (real DB) |
|---|---|---|---|
| Stock badges | `frontend/src/components/ProductCard.tsx` | Badge computed from the card's real `inventory` rows (low stock = 1–3) | Baseball Left Chest Crewneck → "Sold out in XS, XL" (XS = 0, XL = 0) ✅ |
| "Ask DD about this" | `pages/ProductDetail.tsx`, `askDD.ts`, `components/ChatWidget.tsx` | Chips dispatch a `cc:ask-dd` event; the chat opens and sends the question with the page context, so "this" = the product | Yale Mom Hoodie, M → "8 in stock, $68.00" ✅ |
| Find alternatives | `backend/tools.py` `find_alternatives`, `models.py` `Alternatives` | Same garment family, quantity > 0 in the wanted size, ranked by shared colours → price → stock; the prompt tells DD to call it on `sold_out` | Baseball crewneck XL (0) → 3 similar $58 crewnecks in stock in XL ✅ |
| Remember size | `backend/preferences.py`, `agent.py` `remember_preferences`, `ShopDeps.preferences` | New `customer_preferences` table (one row per user); loaded into agent deps each logged-in turn | "I usually wear a medium and I love navy" → saved M/navy; later "is this in stock for me?" → "your usual medium… 8 available" ✅ |
