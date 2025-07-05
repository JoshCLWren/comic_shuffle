# 📚 Comic Shuffle

A mobile-friendly Streamlit app built in Python to help you pick your next comic to read from a curated reading list. Prioritizes shorter reading orders to help you finish your runs faster.

## 🚀 Features

- ✅ Shake-free "🎲 Shuffle Comic" button
- ✅ Balanced selection that favors shorter reading orders
- ✅ Tap "✅ Mark as Read" to track your progress
- ✅ Easy-to-edit JSON reading list
- ✅ Mobile-friendly and deployable via [Streamlit Cloud](https://streamlit.io/cloud)

---

## 📦 Requirements

- Python 3.10 or 3.11
- Streamlit >= 1.35

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the App

```bash
streamlit run streamlit_app.py
```

---

## 📁 Project Structure

```
.
├── reading_orders.json       # Your reading list data
├── streamlit_app.py          # The Streamlit UI and logic
├── requirements.txt          # Streamlit dependency
└── README.md                 # This file
```

---

## 🧠 JSON Format

Each reading order has a label and a list of entries:

```json
{
  "comics": [
    {
      "label": "X-men Reading Order",
      "entries": [
        { "comic": "Excalibur 106", "status": "unread" },
        { "comic": "Magneto 1", "status": "unread" }
      ],
      "format": "singles",
      "category": "main"
    }
  ]
}
```

---

## ☁️ Deploying to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect your GitHub and deploy the app

Enjoy never overthinking your next comic again! 🦸📖
