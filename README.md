# 🌍 Travel Weather Planner

AI-powered travel advisor with a modern web interface. Get weather-based recommendations using OpenAI's function calling and real-time weather data.

## Features

✨ **Smart Date Parsing** - Understands "next month", "in 2 weeks", etc.  
🌡️ **Historical Weather Data** - Uses Open-Meteo API for accurate climate info  
🗺️ **Global Coverage** - Works for any city worldwide  
🤖 **LLM-Powered Advice** - Personalized packing lists and activity recommendations  
🔧 **Function Calling** - No hallucination - LLM uses real tools for accurate data  
💻 **Modern Web UI** - Beautiful, responsive interface with real-time updates

## Setup

### 1. Install Dependencies

```bash
# Activate your virtual environment
.\virtual\Scripts\Activate.ps1  # Windows PowerShell
# or
source virtual/bin/activate      # Linux/Mac

# Install required packages
pip install -r requirements.txt
```

### 2. Configure API Key

```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. Start the Application



### 4. Open Your Browser

Navigate to: **http://localhost:8000**

## Usage

### Web Interface (Recommended)
1. Open http://localhost:8000 in your browser
2. Type your travel question in the chat
3. Watch as the AI uses tools in real-time to gather data
4. Get personalized travel advice!

### Example Queries
- "I'm planning a trip to Tokyo for next month"
- "What's the weather like in Paris in 2 weeks?"
- "Should I bring an umbrella to London next month?"
- "I want to visit Bali in 3 months, what should I pack?"

### API Endpoints

**Health Check:**
```bash
GET http://localhost:8000/api/health
```

**REST Chat (non-streaming):**
```bash
POST http://localhost:8000/api/chat
Content-Type: application/json

{
  "message": "I'm planning a trip to Tokyo for next month"
}
```

**WebSocket Chat (real-time streaming):**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat');
ws.send(JSON.stringify({ message: "Your question here" }));
```

## Architecture

```
Frontend (HTML/CSS/JS)
    ↓ WebSocket
FastAPI Backend
    ↓ Tool Calling
OpenAI API
    ↓ Parallel Execution
[get_current_date] [calculate_dates] [get_coordinates] [get_weather]
    ↓
LLM Analysis → Travel Advice
```

## Tech Stack

- **Backend**: FastAPI + WebSocket for real-time communication
- **Frontend**: Vanilla JavaScript with modern CSS
- **AI**: OpenAI GPT-4o-mini with function calling
- **APIs**: Open-Meteo (weather), Nominatim (geocoding)

## Why FastAPI (Not Flask)?

- ✅ **Native WebSocket support** - Real-time streaming
- ✅ **Async/await** - Better performance for I/O operations
- ✅ **Auto-generated docs** - Built-in Swagger UI at `/docs`
- ✅ **Type hints** - Better code quality with Pydantic
- ✅ **Modern & fast** - Built on Starlette and Uvicorn

## Project Structure

```
travel-weather-planner/
├── app.py                    # FastAPI backend server
├── travel_weather_planner.py # Core functions and tools
├── static/
│   ├── index.html           # Main web interface
│   ├── style.css            # Modern UI styling
│   └── script.js            # WebSocket client & UI logic
├── requirements.txt          # Python dependencies
├── .env                     # API keys (create this)
├── start.ps1                # Windows startup script
└── start.sh                 # Linux/Mac startup script
```

## API Credits

- **Weather Data**: [Open-Meteo](https://open-meteo.com/) (Free, no key required)
- **Geocoding**: [Nominatim](https://nominatim.org/) (OpenStreetMap, free)
- **LLM**: OpenAI GPT-4o-mini

## Cost Estimate

- ~$0.001-0.003 per query (GPT-4o-mini)
- Weather/geocoding APIs: Free
- **Monthly cost**: ~$1-5 for moderate use

## Troubleshooting

**"OPENAI_API_KEY not found"**
- Check `.env` file exists in project root
- Ensure key starts with `sk-`

**"Could not find coordinates"**
- Try more specific city names: "Paris, France" vs just "Paris"

**WebSocket connection failed**
- Make sure the server is running
- Check firewall settings
- Try `http://localhost:8000` instead of `127.0.0.1`

**"Port 8000 already in use"**
- Change port in start script: `--port 8001`
- Or stop the process using port 8000

## Development

**Run with auto-reload:**
```bash
uvicorn app:app --reload
```

**Access API docs:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT
