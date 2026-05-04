# 🏦 Inam's Digital Bank API (FastAPI + Supabase)

A secure Pakistani Fintech API built for peer-to-peer transfers, bill payments, and real-time balance inquiries.

## 🚀 Live Links
*   **Backend API URL:** [https://mini-bank-api-ll4k.onrender.com](https://mini-bank-api-ll4k.onrender.com)
*   **Interactive Documentation:** [https://mini-bank-api-ll4k.onrender.com/docs](https://mini-bank-api-ll4k.onrender.com/docs)
*   **Frontend (Lovable):** [Paste your Lovable deployment URL here once published]

## 🛠️ Tech Stack
*   **Framework:** FastAPI (Python)
*   **Database:** PostgreSQL (Supabase)
*   **Authentication:** JWT (JSON Web Tokens)
*   **Deployment:** Render
*   **ORM:** SQLAlchemy

## ✨ Key Features
- ✅ **Secure Signup/Login:** Password hashing and JWT authentication.
- ✅ **P2P Transfers:** Transfer PKR between accounts using phone numbers.
- ✅ **Balance Inquiry:** Real-time balance updates.
- ✅ **Daily Limits:** Safety check for transfers exceeding 50,000 PKR.
- ✅ **Bill Payments:** Fetch and pay utility bills (KE, SNGPL, etc.).
- ✅ **Transaction History:** Full audit trail of sent and received payments.

## ⚙️ Environment Variables Required
To run this project, you must set up the following environment variables in your `.env` or Render settings:
- `DATABASE_URL`: Your Supabase PostgreSQL connection string.
- `SECRET_KEY`: A secure random string for JWT signing.
- `ALGORITHM`: Usually `HS256`.

## 📖 How to Run Locally
1. Clone the repo: `git clone [YOUR_REPO_URL]`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `uvicorn main:app --reload`