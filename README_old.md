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
```

### 2. Setup environment

If running locally:

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

If using **GitHub Codespaces**, everything is preconfigured via `.devcontainer/`.

### 3. Configure Supabase

1. Create a [Supabase project](https://supabase.com/dashboard).
2. Copy your **Project URL** and **anon/public API key**.
3. Add them to a `.streamlit/secrets.toml` file:

   ```toml
   [supabase]
   url = "https://your-project.supabase.co"
   anon_key = "your-anon-key"
   ```

### 4. Run the app

```bash
streamlit run app.py
```

The app will open at [http://localhost:8501](http://localhost:8501).

---

## 📂 Project Structure

```
toolshare/
├── app.py                # Main Streamlit app
├── requirements.txt      # Python dependencies
├── .devcontainer/        # Codespaces dev environment
│   └── devcontainer.json
├── .streamlit/
│   └── secrets.toml      # Supabase credentials (not committed!)
└── README.md
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
