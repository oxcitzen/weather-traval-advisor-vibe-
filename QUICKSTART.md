# 🚀 Quick Setup Guide

## 1️⃣ Install Dependencies

```powershell
# Activate virtual environment (you already have this)
.\virtual\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

## 2️⃣ Configure API Key

```powershell
# Copy example file
copy .env.example .env

# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-your-key-here
```

## 3️⃣ Start the Server

```powershell
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## 4️⃣ Open Your Browser

Go to: **http://localhost:8000**

---

## 📁 File Structure

```
your-project/
├── app.py                     ← FastAPI server (backend)
├── travel_weather_planner.py  ← Core functions
├── static/
│   ├── index.html            ← Web interface
│   ├── style.css             ← Styling
│   └── script.js             ← Frontend logic
├── .env                      ← API key (create this!)
├── requirements.txt
└── start.ps1                 ← Startup script
```

---

## 💡 Example Queries

Try these in the web interface:

- "I'm planning a trip to Tokyo for next month"
- "What's the weather like in Paris in 2 weeks?"
- "Should I bring an umbrella to London next month?"
- "I want to visit Bali in 3 months"

---

## 🔧 Troubleshooting

**Can't connect to server?**
- Make sure server is running: `.\start.ps1`
- Check http://localhost:8000 (not 127.0.0.1)

**API key error?**
- Check `.env` file exists
- Verify key starts with `sk-`

**Port already in use?**
- Change port: `python -m uvicorn app:app --port 8001`

---

## 📊 How It Works

1. You type: "I want to visit Tokyo next month"
2. WebSocket sends message to FastAPI backend
3. Backend calls OpenAI with function calling enabled
4. LLM decides which tools to use:
   - `get_current_date()` → Knows today
   - `calculate_travel_dates(months_ahead=1)` → Gets April dates
   - `get_city_coordinates("Tokyo")` → Gets lat/lon
   - `get_historical_weather(...)` → Gets weather data
5. LLM analyzes all data and streams response back
6. You see real-time updates in browser!

---

That's it! Enjoy your travel weather planner! 🌍✈️
