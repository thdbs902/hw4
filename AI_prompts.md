# HW4 — AI Prompts Log

This file records the prompts I typed to my vibe coder (Claude Code) while working on HW4, one section per problem. Quoted blocks are my prompts exactly as I typed them; follow-up prompts include a one-sentence note on what was lacking before.

---

## Setup instructions

These are the general instructions I gave before starting the problems (not a problem prompt).

> HW4
>
> plz first read the whole assignment and understand the project structure before changing anything.
>
> * use my `PORTKEY_API_KEY`
> * use OpenAI model `gpt-5.6-luna` through Portkey
> * work one problem at a time
> * do not jump ahead unless something is necessary for the current problem
> * keep my existing files/content when later problems ask you to update them; add to them instead of replacing useful work
> * send me a silver heart emoji 🩶 if you understand my instructions, every time
> * if something I ask will take more than 3 minutes, tell me before you start it
> * remember that my code, JSON outputs, running app, database writes, and screenshots are the evidence that I completed the work myself
> * do not commit my real `.env`, `campus_customs.db`, or product images
> * when you change something, ask me to allow it and do not change the prompt by yourself. this is my homework
>
> Work with me step by step. Do not start Problem 2 until I tell you to.

---

## Problem 1 — Vibe coder prompts

**Prompt 1**

> plz do Problem 1 first
>
> * create `AI_prompts.md` in my HW4 project
> * use this file to keep the prompts I actually type to you while doing this assignment
> * make one section for each problem with the problem number and title
> * for each problem, include at least one prompt I actually typed in my own words
> * if I need a follow-up prompt, add that too and briefly say what was lacking after the first prompt
> * do not invent prompts that I didn't actually give you
> * keep updating this same file as we work through the assignment instead of replacing it
>
> for now just set this up for Problem 1 and don't start Problem 2 yet
> also remember the actual database structure you just found because we will need it in later problems

**Prompt 2 (follow-up)**

*What was lacking:* the first prompt didn't give the official problem title or say how to handle my setup instructions and simple verification messages in the log.

> for Problem 1:
>
> * the official title is `Vibe coder prompts`
> * create `AI_prompts.md` now
> * keep a simple heading/intro if useful, but don't present your own words as words I typed
> * record the actual Problem 1 prompt I gave you
> * you don't need to log simple verification/checking messages as follow-up prompts unless they actually change, correct, or add something substantive to the implementation
> * if I give a real follow-up because something was missing or wrong, then log it and add the required one-sentence explanation of what was lacking
> * you may keep my initial assignment setup instructions in a clearly labeled `Setup instructions` section since I actually typed them, but don't treat them as the required Problem 1 prompt
> * remember the real database structure you already inspected and use it in later problems

---

## Problem 2 — Analyze the database

**Prompt 1**

> Problem 2 — Analyze the database
> plz inspect `data/campus_customs.db` directly and document the actual database I have, not just what the handout says should be there.
>
> * inspect all tables and their real schema, especially `catalogue`, `inventory`, `users`, and the existing `chat_messages` table you already found
> * create `output/harness.md`
> * list each table and its actual fields
> * for each field, add one short line explaining why it matters for the shop or chatbot
> * note useful relationships between tables, such as how product IDs connect catalogue and inventory and how user IDs connect to chat history, if those relationships are actually supported by the database
> * mention important existing data/setup that will affect later problems, such as the existing hashed passwords, existing chat history table, and image paths being relative to `data/`
> * do not modify, delete, or add database data for this problem
> * don't invent fields or relationships that aren't actually in SQLite
> * keep `output/harness.md` as the same growing harness file for later problems; later work should add/update sections instead of replacing useful existing content
> * update the Problem 2 section of `AI_prompts.md` with this actual prompt
>
> when you're done, briefly tell me what files you created or changed and any database detail that could affect later problems. then stop before Problem 3.

---

## Problem 3 — Build the CC website

**Prompt 1**

> [Problem 3: Build the CC website (10 points)]
> plz
>
> * scaffold a React + Vite + TypeScript front end for CC
> * add a nav bar at the top that links to the main pages
>    * Home
>    * Products
>    * About Us
>    * Log in
>    * Create account
> * research `yalebulldogblue.com` to learn the style of CC page and information
> * write the Home and About Us pages in my own voice
>    * do not copy the original site text
> * show product images from the catalogue on the Products page
>    * use the image paths in the database
>    * show name, price, and short description
> * make each product card open a single-item page
>    * show a large image on one side
>    * show full product text on the other side
>    * include description, price, and size / stock when available
> * add a chat interface in the bottom right of the site
>    * a floating chat panel is fine
>    * it does not need to talk to an agent yet
>    * a stub that will call my backend later is enough
> * create a simple FastAPI app in `backend/main.py` if needed to read the database and serve products and images
>    * we will grow this into the agent backend in Problem 5
> * use the actual `data/campus_customs.db` and `data/products/` I already have
> * keep updating `AI_prompts.md` with the prompt I actually give you
> * run the front end and backend when finished and give me the local link so I can check the website myself
> * do not start Problem 4 yet

**Prompt 2 (follow-up)**

*What was lacking:* the first build showed many product photos on black backgrounds with a white halo, the product cards didn't make the detail page obvious, and the colours couldn't be clicked.

> plz
>
> * check if Problem 3 meets everything in the assignment
> * test the pages, product images, product detail page and chat
> * fix anything missing before Problem 4
>
> like for example, I don't want to see the black background of product image because I can see the white silouette. I can't find detailed information page, neither. I can't click each color, too.

---

## Problem 4 — Create account and login

**Prompt 1**

> [Problem 4: Create account and login (8 points)]
> plz
>
> * build a normal create-account / login flow
> * make the create-account page ask for
>    * first name
>    * last name
>    * email
>    * password
>    * confirm password
> * make the login page ask for
>    * email
>    * password
> * save new accounts into the existing `users` table
> * store passwords securely so hackers, human or AI, cannot access them
>    * do not store plain text passwords
> * use the existing test user to test the login
>    * email: `test@campuscustoms.yale.edu`
>    * password: `password`
> * confirm the existing test user can log in
> * create a brand-new account and confirm that account can also log in
> * use the existing database structure I already have and do not remove the existing users
> * update `output/harness.md` with
>    * what I store for a user
>    * how passwords are protected
> * keep my existing harness content and add to it rather than replacing it
> * keep updating `AI_prompts.md` with the prompt I actually give you
> * do not start Problem 5 yet
>
> * you must let me know if you think you will take more than 3 minutes for prompting

---

## Problem 5 — PydanticAI agent backend

**Prompt 1**

> [Problem 5: PydanticAI agent backend (12 points)]
> plz
>
> * build the shop chatbot as a PydanticAI agent behind FastAPI
> * connect the agent to my existing front-end chat widget
> * put the FastAPI app in `backend/main.py`
>    * this is the file I will run with Uvicorn
> * keep the agent in these four files next to it
>    * `backend/prompts/prompt.md` - system prompt
>    * `backend/agent.py` - agent entry / wiring
>    * `backend/tools.py` - tools the agent can call
>    * `backend/models.py` - Pydantic / PydanticAI structured types
> * expose a chat route in `main.py`
>    * a message from the website should return a reply from the agent
>    * keep whatever else I already need for products and auth
> * use my `PORTKEY_API_KEY`
> * use OpenAI model `gpt-5.6-luna` through Portkey
> * use `backend/prompts/prompt.md` for the agent system prompt
> * add CC voice and basic safety rules to `prompts/prompt.md`
>    * we will expand the tools and safety later
> * create or update types in `models.py` for chat replies / product cards as needed
>    * keep my existing models if I already have any
> * update `output/harness.md` with
>    * how the front end talks to FastAPI
>    * how the agent is loaded
>    * the prompt file
>    * the model
> * keep my existing harness content and add to it rather than replacing it
> * make sure the backend runs from the `backend/` folder with
>    * `uvicorn main:app --reload --port 8000`
> * test the chatbot from the website and make sure I get a real agent response
> * keep updating `AI_prompts.md` with the prompt I actually give you
> * do not start Problem 6 yet

**Prompt 2 (follow-up)**

*What was lacking:* the first version returned an error instead of a polite reply when the provider's safety filter blocked a jailbreak-style message, and there was no visible proof in the logs that website chats were going through the PydanticAI agent's tools.

> plz
>
> * check if Problem 5 meets everything in the assignment
> * test the chatbot from the website and make sure it is actually using the PydanticAI agent
> * fix anything missing before Problem 6

---

## Problem 6 — Tools: product info and stock

**Prompt 1**

> [Problem 6: Tools: product info and stock (8 points)]
> plz
>
> * give the agent tools that look up real information from `campus_customs.db`
> * make the tools look up
>    * product description
>    * price
>    * how many are in stock
>    * stock by size when the customer asks about a size
> * make the agent use the database for product information
>    * do not invent prices or quantities
> * make the agent say clearly when a size is out of stock
> * use the actual inventory structure I already have
>    * check the specific size before saying that an item is available
> * expand `prompts/prompt.md` so the agent knows to call these tools for price and stock questions
> * add or update return types in `models.py` as needed
>    * keep my existing models
> * update `output/harness.md` with
>    * each tool the agent can use
>    * which model fields I chose for the lookup results
>    * why I chose those fields
> * keep my existing harness content and add to it rather than replacing it
> * test the tools using actual products, prices and inventory from my database
> * keep updating `AI_prompts.md` with the prompt I actually give you
> * do not start Problem 7 yet

**Prompt 2 (follow-up)**

*What was lacking:* when a product didn't exist, the agent asked the shopper for a photo (it can't see images) and its "closest" suggestions were unrelated items. It also repeated identical searches, and the prompt didn't explicitly list the facts the database doesn't have (fabric, care, restock dates).

> plz
>
> * check if Problem 6 meets everything in the assignment
> * compare the agent's price and stock answers with the actual database
> * make sure it does not invent any product information
> * fix anything missing before Problem 7

---

## Problem 7 — Chat search that updates the page

**Prompt 1**

> [Problem 7: Chat search that updates the page (10 points)]
> plz
>
> * add a feature so the agent can search the catalogue when a customer asks about a type of item
>    * for example, `"what hoodies do you have?"`
> * make the agent return structured product matches
> * make the front end dynamically show the matching items as product cards
> * show on each product card
>    * image
>    * name
>    * price
>    * short product information
> * use the actual products from `campus_customs.db`
> * make the structured product matches from the agent reach the front end through the API
> * keep the same single-item page behavior from Problem 3 for the new dynamic product cards
>    * make each chat-generated product card clickable
>    * make it open the product detail page with the large image and full product information
> * update `prompts/prompt.md` so the agent knows how to handle product search questions
> * update `output/harness.md` with
>    * how the search results reach the page
>    * how the structured product matches are used by the front end
> * keep my existing harness content and add to it rather than replacing it
> * test the feature with an actual product type from my database
> * keep updating `AI_prompts.md` with the prompt I actually give you
> * do not start Problem 8 yet

---

## Problem 8 — Customer memory

**Prompt 1**

> [Problem 8: Customer memory (8 points)]
> plz
>
> * save chat history in the database when a shopper is logged in
> * use the existing `chat_messages` table if it is appropriate
>    * do not create another chat history table if the existing one already works for this problem
> * reload the logged-in shopper's previous chat history when they return
> * let guest users still use the chat
>    * guest chat history does not need to persist
> * make the agent know who is chatting
>    * include the relevant customer name and email
>    * put this in agent deps or use an equivalent clear pattern
> * pass enough current page context to the agent
>    * if a customer is on a product page and asks `"do you have this in pink?"`, make sure the agent knows which product `"this"` means
> * do not give the agent passwords or password hashes
> * update `output/harness.md` with
>    * how user chat history is stored
>    * what customer fields the agent sees
>    * how page context is passed to the agent
> * keep my existing harness content and add to it rather than replacing it
> * test the feature with both a logged-in user and a guest
> * keep updating `AI_prompts.md` with the prompt I actually give you
> * please pace up as much as possible so that I can go to bed I'm so tired
> * do not start Problem 9 yet

---

## Problem 9 — Usability improvements

**Prompt 1**

> [Problem 9: Usability improvements (12 points)]
> plz
>
> * review my current website and choose some possible usability improvements
> * suggest
>    * 3 front-end usability improvements
>    * 3 agent / backend usability improvements
> * focus on improvements that are useful for a CC shopper or the business
> * keep the ideas simple enough to build and test with my current website
> * explain each option very briefly
>    * what it would add
>    * why it would help a CC shopper or the business
> * do not implement them yet
> * let me choose 2 front-end improvements and 2 agent / backend improvements first


**Prompt 2 (follow-up)**

*What was lacking:* I had picked only one improvement per list, and the chosen improvements weren't built yet (Problem 11 needs them working), so I picked the second ones (“Ask DD about this” button, find-alternatives tool) and had all four implemented.

> plz
>
> * check if Problem 9 meets everything in the assignment
> * fix anything missing before Problem 10
> * solve my prompt as fast as possible

---

## Problem 10 — Style the website

**Prompt 1**

> [Problem 10: Style the website (6 points)]
> plz
>
> * add creative design so the site feels like a real CC storefront
> * improve
>    * fonts
>    * colors
>    * visual hierarchy
>    * motion
>    * product presentation
>    * chat feel
> * make the design imaginative and innovative
> * keep the website easy to use and shop
> * keep all the existing features working
> * create `output/design.md`
> * write in `output/design.md`
>    * what I changed
>    * why it should help customers stick around and buy
> * keep the write-up concrete and short
> * keep updating `AI_prompts.md` with the prompt I actually give you
> * do not start Problem 11 yet
> * solve my prompt as fast as possible

**Prompt 2 (follow-up)**

*What was lacking:* the first design kept the navy/gold boutique look, but I wanted a more imaginative Apple × NFL halftime-show theme with click sounds, neater product photos (black backgrounds and outlines trimmed), and Yale college and school branding.

> basic hoodie big yale outline shall be trimmed better. the image doesn't look neat.
>
> * design the website looking like Apple - NFL halftime show theme with even audio clicking sound. use your imagination under this theme

> products dont look neat at all. please trim the background colors as much as possible so that each product looks okay and good for sale.
>
> put the Yale colleage logos and schools logos on top or so CC can show Yale store. the brand name matters here.


**Prompt 3 (follow-up)**

*What was lacking:* the college/school bar used letter monograms instead of the real crests, there was no stadium crowd atmosphere, and the front page had no Handsome Dan mascot.

> I meant the logos for colleges and schools at the front page of webpage with the real logos not with the alphabets. try search harder
> put the background music just like crowds ambivalence (shouting supporting for teams - matching stadium sound 열광하는 소리)
> make Handsome Dan bulldog with a foot ball running around the front web page - looking cute. cute illustrated dog.


**Prompt 4 (follow-up)**

*What was lacking:* the first crowd ambience was a generic noise bed; I wanted it to sound like a real cheering, roaring, chanting, applauding stadium crowd.

> the background sound is cheering crowd roaring chanting applausing sound

---

## Problem 11 — Site testing (app check)

**Prompt 1**

> [Problem 11: Site testing (app check) (8 points)]
> plz
>
> * test the live site
> * document the testing in `output/app_check.html`
>    * make it a page I can double-click and open
> * include clear screenshots and short captions for
>    * chat checking the inventory level of an item
>       * show honest stock / price from the database
>    * dynamic search-result cards appearing after a category question
>       * for example, `"what hoodies do you have?"`
>    * one of the usability features I added in Problem 9
> * use the actual running app for the screenshots
> * put the screenshot image files in `output/app_check_images/`
> * link the screenshots from `app_check.html` with relative paths
>    * for example, `app_check_images/inventory.png`
> * make the HTML easy to grade
>    * add a heading for each check
>    * show the screenshot
>    * add one or two sentences explaining what the screenshot proves
> * make sure the screenshots clearly show that each required feature is actually working
> * keep updating `AI_prompts.md` with the prompt I actually give you
> * do not start Problem 12 yet
> * solve my prompt as fast as possible

---

## Problem 12 — Audit trail, safety, finish harness

**Prompt 1**

> [Problem 12: Audit trail, safety, finish harness (4 points)]
> plz
>
> * create an append-only `output/audit_trail.json`
> * record agent-loop activity with
>    * time
>    * tool name
>    * short args / result
>    * stop reason
> * do not wipe the existing audit trail between runs
> * add safety rules for the agent in `prompts/prompt.md`
> * make sure the safety rules help the agent
>    * use real database information for product facts
>    * not invent prices or stock
>    * protect passwords and private information
>    * not expose API keys or other secrets
> * finish `output/harness.md`
> * include in `output/harness.md`
>    * model fields in `models.py` and why I chose them
>    * tools and abilities
>    * safety rules
>    * specs
>       * loop limits
>       * result caps
>       * models
>       * how to run the front end and back end
> * use the actual values from my code for the specs
> * keep my existing harness content and add to it rather than replacing it
> * keep updating `AI_prompts.md` with the prompt I actually give you
> * do not start Problem 13 yet
> * solve my prompt as fast as possible

---

## Problem 13 — Push to GitHub and submit the URL

**Prompt 1**

> [Problem 13: Push to Github and submit the URL (4 points)]
> plz
>
> * make sure my code is in a folder named `hw4`
> * prepare the project to push to a public GitHub repository
> * make sure the final project includes
>    * `AI_prompts.md`
>    * `requirements.txt`
>    * `.env.example`
>    * `.gitignore`
>    * `README.md`
>    * `frontend/`
>    * `backend/main.py`
>    * `backend/agent.py`
>    * `backend/models.py`
>    * `backend/tools.py`
>    * `backend/prompts/prompt.md`
>    * `output/harness.md`
>    * `output/design.md`
>    * `output/usability.md`
>    * `output/app_check.html`
>    * `output/app_check_images/`
>    * `output/audit_trail.json`
> * do not put these in the GitHub repo
>    * my real `.env`
>    * `campus_customs.db`
>    * product images
>    * any real API keys or secrets
> * use `.gitignore` to keep the local-only data out of GitHub
> * include `.env.example` with placeholders only
> * make `README.md` explain
>    * how to run the front end
>    * how to run the back end
>    * where to place the local data pack
> * check the expected file layout against the assignment
> * push the project to a public GitHub repository
> * give me the final repo URL that I should submit on Canvas
> * keep updating `AI_prompts.md` with the prompt I actually give you
> * solve my prompt as fast as possible
