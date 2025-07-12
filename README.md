# AI Travel Planner v7



<p align="center">
  <img src="https://img.shields.io/badge/Streamlit-1.35.0-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/OpenAI-1.30.0-412991?logo=openai&logoColor=white" alt="OpenAI" />
  <img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/License-MIT-black" alt="License" />
  <img src="https://visitor-badge.glitch.me/badge?page_id=yourusername.ai-travel-planner" alt="visitors" />
</p>



> **Plan smarter trips in seconds – from flights to food, fully costed and explained.**

---

## 🎬 Demo / Live Preview

---

---

## ✨ Features

|                            |                                                    |
| -------------------------- | -------------------------------------------------- |
| 🗺️ **Smart itinerary**    | Generates day‑by‑day plans in JSON for easy re‑use |
| 💰 **Realistic budgets**   | Breakdown of lodging, transport, food, activities  |
| 🔍 **Live web data**       | Scrapes current prices & opening hours on the fly  |
| 🪄 **Pro tips & why**      | Explains every recommendation so you learn         |
| 🚀 **Exports & favorites** | One‑click download or save destinations            |

---

## 🚀 Quick Start

```bash
# clone & install
git clone https://github.com/yourusername/ai-travel-planner-v7.git
cd ai-travel-planner-v7
pip install -r requirements.txt

# add secrets
echo "OPENAI_API_KEY='sk-...'" >> .streamlit/secrets.toml

# run
streamlit run app.py
```

> **Tip:** Add `BRAVE_API_KEY="brv_..."` for richer search results.

---

## 🧭 How to Use

1. **Origin & Destination** – type or pick from history.
2. **Dates, Budget, Interests** – sliders & multiselects keep it friendly.
3. **Model** – choose speed vs. depth.
4. **Generate** – get your plan with costs, maps, & tips.
5. **Export** – JSON/Text or just bookmark it.

---

## 📂 Project Layout

```
ai-travel-planner-v7/
├── app.py                 # Streamlit UI + core logic
├── requirements.txt       # Dependencies
└── .streamlit/
    └── secrets.toml       # API keys (git-ignored)
```

---

## 🛠️ Built With

| Technology         | Use‑case                     |
| ------------------ | ---------------------------- |
| **Python 3.8+**    | Core language                |
| **Streamlit 1.35** | Front‑end + state management |
| **OpenAI 1.30**    | LLM itinerary generation     |
| HTTPX 0.27         | Async web requests           |
| BeautifulSoup 4.12 | HTML parsing & scraping      |
| DuckDuckGo 6.1     | Search API                   |
| DiskCache 5.6      | Local caching                |
| Geopy 2.4          | Geocoding & distance         |
| Plotly 5.17        | Interactive charts           |
| Docker             | Containerised deployment     |

---

## 🌱 Roadmap

* Weather & climate insights
* Smart packing checklist
* Local events + currency converter
* Accounts & cloud save

---

## 📌 Why This Project Stands Out

* **Full‑stack AI**: Shows end‑to‑end use of LLMs, web scraping, caching, and reactive UI.
* **Real users in mind**: Emphasis on budget transparency and actionable tips.
* **Deploy‑ready**: Streamlit Cloud or Docker in minutes.

Perfect for CVs and university applications to demonstrate practical AI, UX, and DevSecOps skills.

---

## 📜 License

MIT – see `LICENSE`.

---

## 🤝 Contact

[Younes Touzani](https://linkedin.com/in/younes-touzani) · [youness@example.com](mailto:youness@example.com)
Feedback and PRs welcome!

---

*Crafted with ❤️ to help travelers explore more and worry less.*
