"""
Travel Weather Planner - OpenAI Tool Calling Integration
Uses OpenAI API directly for clean, maintainable code.
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =====================================================
# DATE FUNCTIONS
# =====================================================

def get_current_date():
    """
    Get the current date.
    
    Returns:
        dict: Current date information
    """
    now = datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "month_name": now.strftime("%B"),
        "formatted": now.strftime("%B %d, %Y")
    }


def calculate_travel_dates(months_ahead=0, days_ahead=0, weeks_ahead=0):
    """
    Calculate future dates based on current date + offset.
    
    Args:
        months_ahead: Number of months to add
        days_ahead: Number of days to add
        weeks_ahead: Number of weeks to add
    
    Returns:
        dict: Date range information
    """
    import calendar
    now = datetime.now()
    
    if months_ahead > 0:
        # Calculate target month/year
        month = now.month + months_ahead
        year = now.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1
        
        # Get full month range
        last_day = calendar.monthrange(year, month)[1]
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, last_day)
    else:
        # Add days/weeks
        target_date = now + timedelta(days=days_ahead, weeks=weeks_ahead)
        start_date = target_date
        end_date = target_date
    
    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "month_name": start_date.strftime("%B"),
        "year": start_date.year
    }


# =====================================================
# GEOCODING FUNCTION
# =====================================================

def get_city_coordinates(city_name):
    """
    Convert city name to latitude and longitude.
    
    Args:
        city_name: City name (e.g., "Tokyo" or "Paris, France")
    
    Returns:
        dict: Coordinates and city info
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {'q': city_name, 'format': 'json', 'limit': 1}
    headers = {'User-Agent': 'TravelWeatherPlanner/1.0'}
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    if not data:
        return {"error": f"Could not find coordinates for {city_name}"}
    
    return {
        "city": data[0].get('display_name', city_name),
        "latitude": float(data[0]['lat']),
        "longitude": float(data[0]['lon'])
    }


# =====================================================
# WEATHER FUNCTION
# =====================================================

def get_historical_weather(latitude, longitude, start_date, end_date):
    """
    Get historical weather data from Open-Meteo API.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        dict: Weather statistics and data
    """
    # Fetch weather from last year (same period)
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Use last year's data as historical reference
    historical_start = start.replace(year=start.year - 1)
    historical_end = end.replace(year=end.year - 1)
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": historical_start.strftime("%Y-%m-%d"),
        "end_date": historical_end.strftime("%Y-%m-%d"),
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max",
        "timezone": "auto"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'daily' not in data:
        return {"error": "Could not fetch weather data"}
    
    # Calculate statistics
    temps_max = data['daily']['temperature_2m_max']
    temps_min = data['daily']['temperature_2m_min']
    precipitation = data['daily']['precipitation_sum']
    windspeed = data['daily']['windspeed_10m_max']
    
    return {
        "period": f"{start_date} to {end_date}",
        "historical_reference": f"{historical_start.strftime('%Y-%m-%d')} to {historical_end.strftime('%Y-%m-%d')}",
        "temperature": {
            "avg_high": round(sum(temps_max) / len(temps_max), 1),
            "avg_low": round(sum(temps_min) / len(temps_min), 1),
            "max": round(max(temps_max), 1),
            "min": round(min(temps_min), 1),
            "unit": "°C"
        },
        "precipitation": {
            "total_mm": round(sum(precipitation), 1),
            "rainy_days": sum(1 for p in precipitation if p > 1.0),
            "avg_daily_mm": round(sum(precipitation) / len(precipitation), 1)
        },
        "wind": {
            "avg_max_speed": round(sum(windspeed) / len(windspeed), 1),
            "unit": "km/h"
        },
        "summary": f"Based on historical data from the same period last year"
    }


# =====================================================
# TOOL DEFINITIONS FOR OPENAI
# =====================================================

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Get today's date. Always call this first to know the current date before calculating future travel dates.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_travel_dates",
            "description": "Calculate the date range for travel based on relative time from today (e.g., 'next month' = 1 month ahead, 'in 2 weeks' = 2 weeks ahead).",
            "parameters": {
                "type": "object",
                "properties": {
                    "months_ahead": {
                        "type": "integer",
                        "description": "Number of months from today (e.g., 1 for 'next month', 2 for 'in 2 months')"
                    },
                    "days_ahead": {
                        "type": "integer",
                        "description": "Number of days from today"
                    },
                    "weeks_ahead": {
                        "type": "integer",
                        "description": "Number of weeks from today (e.g., 1 for 'next week')"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_city_coordinates",
            "description": "Get latitude and longitude coordinates for a city name. Required before fetching weather data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city_name": {
                        "type": "string",
                        "description": "Name of the city (e.g., 'Tokyo', 'Paris, France', 'New York, USA')"
                    }
                },
                "required": ["city_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_historical_weather",
            "description": "Get historical weather data for a location and date range. Use this to understand typical weather patterns for travel planning.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude coordinate from get_city_coordinates"
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude coordinate from get_city_coordinates"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format from calculate_travel_dates"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format from calculate_travel_dates"
                    }
                },
                "required": ["latitude", "longitude", "start_date", "end_date"]
            }
        }
    }
]


# =====================================================
# FUNCTION DISPATCHER
# =====================================================

available_functions = {
    "get_current_date": get_current_date,
    "calculate_travel_dates": calculate_travel_dates,
    "get_city_coordinates": get_city_coordinates,
    "get_historical_weather": get_historical_weather
}


# =====================================================
# MAIN CHAT FUNCTION
# =====================================================

def chat_with_travel_planner(user_message, conversation_history=None):
    """
    Main function to interact with the travel planner.
    
    Args:
        user_message: User's travel query
        conversation_history: Previous messages (optional)
    
    Returns:
        str: AI's travel advice
    """
    if conversation_history is None:
        conversation_history = []
    
    # Add system message if this is the first message
    if not conversation_history:
        conversation_history.append({
            "role": "system",
            "content": """You are a helpful travel weather advisor. Your job is to:
1. First, get the current date using get_current_date()
2. Calculate travel dates based on user input using calculate_travel_dates()
3. Get coordinates for the destination city using get_city_coordinates()
4. Fetch historical weather data using get_historical_weather()
5. Provide comprehensive travel advice including:
   - What to pack based on expected weather
   - Best activities for the weather conditions
   - Any weather-related warnings or tips
   - Best times of day for outdoor activities

Always use the tools to get accurate data. Never guess dates or weather information."""
        })
    
    # Add user message
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    # Initial API call
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-4o" for more advanced reasoning
        messages=conversation_history,
        tools=tools,
        tool_choice="auto"
    )
    
    # Handle tool calls
    max_iterations = 10  # Prevent infinite loops
    iteration = 0
    
    while response.choices[0].message.tool_calls and iteration < max_iterations:
        iteration += 1
        
        # Add assistant's response to history
        assistant_message = response.choices[0].message
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in assistant_message.tool_calls
            ]
        })
        
        # Execute each tool call
        for tool_call in assistant_message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"🔧 Calling: {function_name}({function_args})")
            
            # Call the function
            function_response = available_functions[function_name](**function_args)
            
            # Add function response to history
            conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(function_response)
            })
        
        # Get next response from OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation_history,
            tools=tools,
            tool_choice="auto"
        )
    
    # Get final answer
    final_answer = response.choices[0].message.content
    conversation_history.append({
        "role": "assistant",
        "content": final_answer
    })
    
    return final_answer, conversation_history


# =====================================================
# EXAMPLE USAGE
# =====================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🌍 TRAVEL WEATHER PLANNER")
    print("=" * 60)
    
    # Example queries
    queries = [
        "I'm planning a trip to Tokyo for next month. What should I expect?",
        "What's the weather like in Paris in 2 months?",
        "I want to visit London next week. What should I pack?"
    ]
    
    for query in queries:
        print(f"\n📝 User: {query}")
        print("-" * 60)
        
        response, _ = chat_with_travel_planner(query)
        print(f"🤖 Assistant: {response}\n")
