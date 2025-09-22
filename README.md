# 🛠️ ToolShare

**Connected Worlds Hackathon 2025 — Team Project**

ToolShare is a community-driven web app that helps neighbors **share tools and equipment**. Instead of buying items that are rarely used, people can lend and borrow from each other — saving money, reducing waste, and building stronger local connections.

This project is built for the hackathon theme:
**“Connected Worlds: Innovating Together”** 🌍

> *Uniting communities through creativity and code.*

---

## 🚀 Features

* 🔎 **Browse tools** available in your community
* ➕ **Add a tool** you’re willing to lend
* 📅 **Reserve tools** from others
* 👤 **User accounts & authentication** (via Supabase)
* 🌱 Promotes sustainability through sharing & reuse

---

## 🛠️ Tech Stack

* [**Streamlit**](https://streamlit.io/) — UI framework (Python-based)
* [**Supabase**](https://supabase.com/) — Database + Auth (Postgres with APIs)
* [**Python 3.11**](https://www.python.org/) — Core programming language
* [**GitHub Codespaces**](https://github.com/features/codespaces) — Cloud development environment

---

## 📦 Setup & Installation

### 1. Clone the repo

```bash
git clone https://github.com/<your-team>/toolshare.git
cd toolshare
```text

### 2. Setup environment

If running locally:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

pip install -r requirements.txt
```python

If using **GitHub Codespaces**, everything is preconfigured via `.devcontainer/`.

### 3. Configure Supabase

1. Create a [Supabase project](https://supabase.com/dashboard).
2. Copy your **Project URL** and **anon/public API key**.
3. Add them to a `.streamlit/secrets.toml` file:

   ```toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your-anon-key"
   ```

### 4. Run the app

```bash
streamlit run app.py
```

The app will open at [http://localhost:8501](http://localhost:8501).

---

## 📂 Project Structure

```
tool-share-app/
├── requirements.txt
├── .devcontainer/
├── .streamlit/
│   └── secrets.toml      # Supabase credentials (not committed!)
└── webapp/
   ├── frontend.py       # Streamlit UI
   ├── backend_K.py      # Basic client init
   └── backend_V.py      # Full auth helpers (email/password, OTP, OAuth)
```

## 🔐 Auth helpers (backend_V)

Examples for the functions in `webapp/backend_V.py`:

```python
from webapp import backend_V as auth

# Email/password signup
auth.sign_up_email_password(
   email="user@example.com",
   password="StrongPass123!",
   first_name="Ada",
   last_name="Lovelace",
)

# Email/password sign-in
auth.sign_in_email_password("user@example.com", "StrongPass123!")

# Phone OTP
auth.send_phone_otp("+15551234567")
# After user receives SMS code
auth.verify_phone_otp("+15551234567", token="123456")

# Email OTP (magic link / code)
auth.send_email_otp("user@example.com")
# If using code method
auth.verify_email_otp("user@example.com", token="123456")

# OAuth (Google, GitHub, etc.)
resp = auth.sign_in_with_oauth("google", redirect_to="http://localhost:8501")
oauth_url = resp["data"]["url"]

# Exchange code after redirect (PKCE)
auth.exchange_code_for_session(auth_code)

# Session helpers
auth.get_user()
auth.set_session(access_token, refresh_token)
auth.sign_out()
```

---

## 👥 Team

* Vidyut Santhosh
* \[Add teammates here]

---

## 🌍 Hackathon Theme Alignment

ToolShare connects communities by:

* Building **trust & collaboration** among neighbors
* Supporting **sustainability** via shared resources
* Reducing **environmental impact** (fewer items manufactured/discarded)

---

## 📜 License

This project is open-sourced under the [MIT License](LICENSE).

---

Would you like me to also include a **sample `app.py` skeleton** (with Supabase connection + simple tool listing/adding) so your team can start coding directly?
