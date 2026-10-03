# Campus Customs (CC) — HW4

A Campus Customs storefront for Yale merch with **DD**, a PydanticAI shopping agent.

- **Front end:** React + Vite + TypeScript (`frontend/`). Home, Products, product detail pages, About Us, Log in / Create account, a floating DD chat, and chat-driven product cards ("DD's picks").
- **Back end:** FastAPI (`backend/main.py`) + a PydanticAI agent (`backend/agent.py`, `tools.py`, `models.py`, `prompts/prompt.md`) using OpenAI **`gpt-5.6-luna` through Portkey**. Prices and stock always come from the local SQLite database.
- Docs: `AI_prompts.md` (my prompts), `output/harness.md` (database, API, agent, tools, safety, specs), `output/design.md`, `output/usability.md`, `output/app_check.html` (open by double-clicking), `output/audit_trail.json`.

## 1. Put the local data pack in place (not in GitHub)

The database and product photos are **not** in this repo. Unzip the course `data.zip` inside this folder so you get:

```
hw4/
└── data/
    ├── campus_customs.db      # catalogue, inventory, users, chat_messages
    └── products/              # product photos (paths match catalogue.image_file_path)
```

`data/` is git-ignored. The scripts below also write cleaned photos (`data/products_clean/`) and Yale crests (`data/brand/`) there.

## 2. Set up secrets

```bash
cp .env.example .env
```

Then edit `.env` with your own `PORTKEY_API_KEY` (and a random `SESSION_SECRET`). `.env` is git-ignored; never commit real keys.

## 3. Run the back end (FastAPI, port 8000)

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r ../requirements.txt
.venv/bin/python clean_images.py   # first time: tidy product photos -> data/products_clean/
.venv/bin/python crop_crests.py    # first time: Yale college/school crests -> data/brand/crests/
.venv/bin/uvicorn main:app --reload --port 8000
```

Optional brand mark: put the Yale University shield SVG at `data/brand/yale-shield.svg` ([Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Yale_University_Shield_1.svg)); the site works without it.

## 4. Run the front end (Vite, port 5174)

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open **http://yalecc.localhost:5174** (or http://127.0.0.1:5174). Any `*.localhost` name points to your own computer in Chrome, so no setup is needed. Vite proxies `/api` and `/media` to the back end on `:8000`.

## Test login

The data pack includes a test user: `test@campuscustoms.yale.edu` / `password`. You can also create a new account on the site; passwords are stored only as salted PBKDF2-SHA256 hashes.

## Layout

```
hw4/
├── AI_prompts.md
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── backend/
│   ├── main.py              # FastAPI app (products, images, auth, chat)
│   ├── agent.py             # DD agent: model, deps, tools wiring, loop limits, audit
│   ├── tools.py             # read-only catalogue + inventory tools
│   ├── models.py            # Pydantic / PydanticAI types
│   ├── prompts/prompt.md    # DD system prompt (voice, tool rules, safety)
│   ├── auth.py  history.py  preferences.py  audit.py
│   └── clean_images.py  crop_crests.py  app_check_screens.py
├── frontend/                # React + Vite + TypeScript
└── output/
    ├── harness.md  design.md  usability.md
    ├── app_check.html  app_check_images/
    └── audit_trail.json     # append-only agent audit trail
```
