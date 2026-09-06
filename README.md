# Staywise — React + Python + MongoDB

A hotel/Airbnb-style booking platform.

- **Frontend:** React + Vite (JavaScript/JSX), plain CSS
- **Backend:** Python + FastAPI
- **Database:** MongoDB (via PyMongo) — replaces the earlier in-memory demo storage
- **Auth:** bcrypt password hashing + JWT bearer sessions, stored per-user in MongoDB
- **Payments:** Razorpay, **Test Mode**, verified server-side (order creation + signature check)
- **Email:** booking-confirmation email sent automatically after a successful payment

---

## 1. What changed from the previous version

| Area | Before | Now |
|---|---|---|
| Storage | Python dict in memory, reset on restart | MongoDB collections: `users`, `hotels`, `bookings` |
| Payment | Fake "Pay & confirm" button, no real gateway | Real Razorpay Checkout (test mode), backend creates the order and verifies the signature before confirming |
| Email | none | Professional HTML confirmation email sent (via SMTP) once payment is verified — fixed bug where it failed to send |
| Registration | Name, email, phone, password | Name, email, password (phone number field removed — email is the only login identifier) |
| Backend layout | one `main.py` | `main.py` (routes) + `config.py`, `db.py`, `security.py`, `payments.py`, `email_utils.py`, `seed_data.py` |

---

## 2. Requirements

- Node.js 20+
- Python 3.10+
- MongoDB 6+ (local install **or** a free MongoDB Atlas cluster — see §4)
- A Razorpay account (free, test mode is enough — see §5)
- (Optional) an email account you can send SMTP mail from, e.g. Gmail with an App Password — see §6

---

## 3. Project structure

```
staywise-python/
  backend/
    main.py            # FastAPI routes
    config.py           # reads all env vars
    db.py                # MongoDB connection + indexes
    security.py         # password hashing, JWT, auth dependencies
    payments.py          # Razorpay order creation + signature verification
    email_utils.py       # booking confirmation email
    seed_data.py         # demo users + demo hotels
    requirements.txt
    .env.example         # copy to backend/.env
  frontend/
    src/
      App.jsx
      api.js
      main.jsx
      index.css
    index.html
    package.json
    vite.config.js
    .env.example         # copy to frontend/.env (usually not needed)
  README.md
  .gitignore
```

---

## 4. MongoDB setup — from absolute scratch

You need a MongoDB database somewhere the backend can connect to. The easiest path for someone doing this for the first time is **MongoDB Atlas** — a free cloud database you set up entirely in a web browser, no installation required. That's what's below, step by step, exactly what to click and type. (A local-install alternative is in §4B if you'd rather not use the cloud.)

You do **not** need to manually create the `users` or `bookings` collections — the backend creates them automatically, with the right structure, the first time it connects (see §4C). You only need to create the empty *cluster* (the server) here.

### 4A. Create the free cluster (do this in your browser)

1. Go to `https://www.mongodb.com/cloud/atlas/register` in your browser.
2. Sign up — either click **"Sign up with Google"** for the fastest path, or fill in email + a password and click the green **"Sign Up"** button. Verify your email if it asks you to.
3. You'll land on a short survey ("What best describes you?" / "What's your goal?"). Pick anything reasonable (e.g. "Learning MongoDB") and click **"Finish"** — it doesn't affect anything technically.
4. You'll now see a screen titled **"Deploy your database"** with a few plan cards. Click the **"M0 FREE"** card (it's the one that says **Free** / **$0** — do not pick a paid tier).
5. Leave **Provider** as AWS (default is fine) and leave the **Region** as whatever is pre-selected (pick one physically close to you if you want, it doesn't matter for this project).
6. At the bottom, you can leave the cluster name as `Cluster0` (default). Click the green **"Create Deployment"** button.

### 4B. Create a database user (username + password for your app to log in with)

Right after creating the cluster, Atlas shows a **"Security Quickstart"** panel:

1. Under **"How would you like to authenticate your connection?"**, keep **"Username and Password"** selected.
2. Type a **username** — e.g. `staywise_app`.
3. Type a **password**, or click **"Autogenerate Secure Password"**. **Copy this password somewhere safe right now** (a notes app) — you'll need it in a moment and Atlas won't show it to you again later.
4. Click the green **"Create Database User"** button.

### 4C. Allow your computer to connect (Network Access)

Still on the same setup screen, under **"Where would you like to connect from?"**:

1. Click **"Add My Current IP Address"** — this lets your current internet connection reach the database.
2. Click **"Finish and Close"**, then on the popup click **"Go to Overview"**.

*(If your internet connection's IP address changes later and the app suddenly can't connect, come back to the left sidebar → **Network Access** → **"+ ADD IP ADDRESS"** → **"Add Current IP Address"** → **Confirm**.)*

### 4D. Get the connection string

1. On the cluster overview page, click the green **"Connect"** button next to your cluster (named `Cluster0`).
2. In the popup, click **"Drivers"** (sometimes labeled "Drivers" under "Connect to your application").
3. Under **"Driver"**, make sure it says **Python**. The **Version** dropdown doesn't matter for this project.
4. Atlas shows a connection string that looks like this:
   ```
   mongodb+srv://staywise_app:<db_password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
   ```
5. Copy that whole string, then replace `<db_password>` with the actual password you saved in step 4B (remove the `<` and `>` characters too).

### 4E. Put it in your project

1. In the project, go to `backend/` and copy `.env.example` to a new file named `.env` in that same folder.
2. Open `backend/.env` in a text editor and set:
   ```
   MONGO_URI=mongodb+srv://staywise_app:YOUR_REAL_PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
   DB_NAME=staywise
   ```
   (Use your actual copied connection string, not this example — the `xxxxx` part is unique to your cluster.)
3. Save the file.

That's it — you don't need to open Atlas again to create collections. When you next run `uvicorn main:app --reload` (see §7), the backend automatically:
- connects using that URI,
- creates a database called `staywise` (from `DB_NAME`),
- creates a `users` collection and a `bookings` collection (and a `hotels` collection) inside it, with the right indexes,
- and inserts the demo accounts/hotels the first time (see §8).

### 4F. (Optional) See the collections with your own eyes

Once you've run the backend once (§7) and it's connected successfully, you can browse the data visually:

1. In Atlas, go to your cluster → click **"Browse Collections"** (button near the cluster name).
2. You'll see a database named **`staywise`** in the left list. Click it to expand.
3. Under it you'll see three collections: **`users`**, **`hotels`**, **`bookings`**. Click any one to see the actual documents (rows) inside — e.g. click `users` to see the demo guest/owner accounts that got seeded, with hashed passwords (never plaintext).
4. As you register new accounts or make bookings through the app, refresh this page and you'll see new documents appear in `users`/`bookings` in real time.

*(If you'd rather use a desktop app instead of the browser for this, MongoDB Compass — `https://www.mongodb.com/try/download/compass` — does the same thing: install it, paste the same connection string from §4D when it asks, and click Connect.)*

### 4B-alt. Prefer a local database instead of the cloud?

If you don't want to use Atlas at all, you can run MongoDB entirely on your own PC instead:

1. Download **MongoDB Community Server** for Windows: `https://www.mongodb.com/try/download/community`.
2. Run the installer. On the **"Setup Type"** screen choose **"Complete"**. Keep **"Install MongoDB as a Service"** checked (this makes it start automatically). You can also check **"Install MongoDB Compass"** on that same screen to get the GUI browser for free.
3. Finish the installer. MongoDB now runs in the background on your machine at port `27017` automatically.
4. In `backend/.env`, use:
   ```
   MONGO_URI=mongodb://localhost:27017
   DB_NAME=staywise
   ```
5. No username or password is needed for a default local install. Collections still get created automatically the same way as §4C above — open MongoDB Compass, connect to `mongodb://localhost:27017`, and you'll see the same `staywise` database with `users`, `hotels`, `bookings` collections once you've run the backend once.


Either way, you don't need to create collections or indexes by hand — the backend creates the `users`, `hotels`, and `bookings` collections and their indexes automatically on first run, and seeds demo data (§8) if the database is empty.

---

## 5. Razorpay test-mode setup

1. Sign up at `https://dashboard.razorpay.com/signup` (free).
2. In the dashboard, make sure the **Test / Live** toggle in the top-right corner is set to **Test**. Everything below happens in Test mode — no real money moves and no business verification is required for testing.
3. Go to **Settings → API Keys → Generate Test Key**.
4. Copy the **Key Id** and **Key Secret** into `backend/.env`:
   ```
   RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxxx
   RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxxxxx
   ```
5. That's it — the frontend never needs its own copy of these keys; the backend hands the (public) Key Id to the frontend per-order when it creates the Razorpay order.

**Testing a payment:** on the Razorpay checkout popup, choose "Card" and use one of Razorpay's published test cards (see `https://razorpay.com/docs/payments/payments/test-card-upi-details/` for the current list), any future expiry date, any 3-digit CVV, and any OTP shown on screen. Card `4111 1111 1111 1111` is Razorpay's commonly documented generic test Visa card — check the docs link above if it stops working, since test card numbers can change.

If `RAZORPAY_KEY_ID`/`RAZORPAY_KEY_SECRET` are left blank, booking creation still works, but the "Pay & confirm" step will return a clear error asking you to configure them — nothing pretends to charge a card without a real (test) gateway behind it.

> **Known packaging issue:** the `razorpay` SDK still imports the old `pkg_resources` module at import time. `setuptools` version 82.0.0+ (Feb 2026) removed `pkg_resources` entirely, so if you see `ModuleNotFoundError: No module named 'pkg_resources'` when starting the API, run `pip install "setuptools<82"`. `requirements.txt` already pins this, but if you ever `pip install --upgrade` things individually, watch out for this one.

---

## 6. Email setup (booking confirmation)

Optional but recommended. If you skip this, bookings still confirm correctly — the backend just logs "would have emailed…" to the console instead of sending anything, so nothing breaks.

### Gmail (recommended for local dev)

1. Turn on 2-Step Verification on the Google account: `https://myaccount.google.com/security`.
2. Create an **App Password**: `https://myaccount.google.com/apppasswords` → choose "Mail" → generate. Copy the 16-character password.
3. In `backend/.env`:
   ```
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=youraddress@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   SMTP_USE_TLS=true
   EMAIL_FROM=youraddress@gmail.com
   EMAIL_FROM_NAME=Staywise
   ```

Any other SMTP provider (Outlook, a transactional service like SendGrid/Mailgun/Amazon SES's SMTP interface, your own mail server) works the same way — just change `SMTP_HOST`/`SMTP_PORT` accordingly.

The email is sent automatically, in the background, right after a Razorpay payment is verified — the guest doesn't wait on it. It's a formatted HTML email (branded header, itemized stay + payment summary, payment reference, support line) with a plain-text fallback for clients that don't render HTML — not a bare text message.

---

## 7. Running it locally

Open two terminals in the project root.

### Terminal 1 — Python API

```bash
cd backend
cp .env.example .env      # then edit .env with your real Mongo/Razorpay/SMTP values
python -m venv .venv

# Windows Command Prompt
.venv\Scripts\activate
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API runs at `http://localhost:8000`. On first start it connects to MongoDB, creates indexes, and seeds demo data if the database is empty (§8). Interactive API docs are available at `http://localhost:8000/docs`.

### Terminal 2 — React frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite dev server proxies `/api` requests to the Python API — you don't need to set `VITE_API_URL` for local development.

---

## 8. Demo data & accounts

The backend seeds these automatically the first time it connects to an empty database (or run `python seed_data.py` from `backend/` any time to seed manually, or `python seed_data.py --force` to wipe and reseed).

Guest login:

```text
Email: guest@staywise.test
Password: demo1234
```

Owner login (use the "Owner" login page):

```text
Email: owner@staywise.test
Password: demo1234
```

---

## 9. API overview

```text
GET    /api/healthz
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me
GET    /api/hotels
GET    /api/hotels/{hotel_id}
GET    /api/bookings
POST   /api/bookings
POST   /api/bookings/{booking_id}/create-order      # creates a Razorpay order (test mode)
POST   /api/bookings/{booking_id}/verify-payment    # verifies signature, marks paid, emails guest
POST   /api/bookings/{booking_id}/cancel
GET    /api/owner/dashboard
GET    /api/owner/bookings
PUT    /api/owner/bookings/{booking_id}/status
POST   /api/owner/hotels
PUT    /api/owner/hotels/{hotel_id}
POST   /api/owner/hotels/{hotel_id}/rooms
```

### Payment flow in detail

1. Guest fills in dates/guests/rooms → `POST /api/bookings` creates a booking with `paymentStatus: "pending"`.
2. Guest clicks **Pay & confirm** → frontend calls `POST /api/bookings/{id}/create-order`.
3. Backend creates a Razorpay order for the booking's *server-computed* total (never trusts an amount from the frontend) and returns the order id + the Razorpay **public** key id.
4. Frontend opens Razorpay's hosted Checkout with that order id.
5. On success, Razorpay hands the frontend a payment id, order id, and signature.
6. Frontend calls `POST /api/bookings/{id}/verify-payment` with those three values.
7. Backend re-verifies the signature against `RAZORPAY_KEY_SECRET` server-side. Only if that check passes does the booking become `paymentStatus: "paid"` / `bookingStatus: "confirmed"`.
8. Backend sends the confirmation email in the background and returns the updated booking; the frontend shows the confirmation screen.

Double-booking protection: room availability is recomputed from existing non-cancelled, non-pending bookings whenever a new booking is created or searched for, using date-overlap logic against `checkIn`/`checkOut`.

---

## 10. Security notes

- Passwords are hashed with bcrypt; the database never stores plaintext passwords.
- JWTs are signed with `SESSION_SECRET` — set a long random value in production (`openssl rand -hex 32` works well).
- Razorpay payments are verified **server-side** using `RAZORPAY_KEY_SECRET`; the frontend never sees the secret, only the public key id.
- `.env` files are git-ignored; only the `.env.example` templates are committed.
- CORS is restricted to `CLIENT_URL` (plus localhost for dev).

## 11. Production notes

- Run `uvicorn` behind a process manager (systemd, Docker, etc.) with multiple workers, e.g. `uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4`.
- Build the frontend for production with `npm run build` (outputs to `frontend/dist`) and serve it from a static host or CDN, pointing `VITE_API_URL` at your deployed API URL before building.
- Switch Razorpay to Live mode by generating **Live** keys in the dashboard and swapping `RAZORPAY_KEY_ID`/`RAZORPAY_KEY_SECRET` — no code changes required.
- Use a real MongoDB Atlas cluster (or a managed MongoDB) rather than a local install.
