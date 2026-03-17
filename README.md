# AnalyticDashAI
### Upload data. Ask anything. See everything.

AI-powered dashboard builder — built on Streamlit + Anthropic Claude API.

---

## Quick Start

```bash
pip install -r requirements.txt
# Add ANTHROPIC_API_KEY to .env or Streamlit secrets
streamlit run app.py
```

## File Structure

```
mcp-data-server/
├── app.py                  ← Main AnalyticDashAI app
├── requirements.txt        ← Python dependencies
├── .streamlit/
│   └── config.toml         ← Brand theme (Signal Orange + Obsidian)
├── data/                   ← Sample datasets
├── screenshots/            ← App screenshots
└── README.md
```

## Features

| Feature | Status |
|---|---|
| Natural language querying | ✅ |
| Auto data cleaning | ✅ |
| 15+ chart types | ✅ |
| AI executive summary ("So What?") | ✅ |
| Anomaly detection | ✅ |
| Role-based dashboard templates | ✅ |
| AI recommendations | ✅ |
| KPI monitoring & snapshots | ✅ |
| CSV / Excel / JSON export | ✅ |
| Multi-sheet Excel support | ✅ |
| Sample dataset built-in | ✅ |

## Brand

- **Primary:** Signal Orange `#FF5C00`
- **Background:** Obsidian `#0C0C0C`
- **Fonts:** Plus Jakarta Sans + Space Grotesk
- **Tagline:** *"Upload data. Ask anything. See everything."*

## Environment

Add to `.env` or Streamlit Cloud secrets:
```
ANTHROPIC_API_KEY=your_key_here
```

## Deploy to Streamlit Cloud

1. Push this repo to GitHub
2. Go to share.streamlit.io → New app
3. Select `app.py` as the main file
4. Add `ANTHROPIC_API_KEY` in secrets

---
Built by Kedarnath · Powered by Anthropic Claude
