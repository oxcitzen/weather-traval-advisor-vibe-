"""
FastAPI Backend for Travel Weather Planner
Handles chat requests and streams responses in real-time
"""

import os
import json
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

from travel_weather_planner import (
    get_current_date,
    calculate_travel_dates,
    get_city_coordinates,
    get_historical_weather,
    tools
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Travel Weather Planner API")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Tool function mapping
available_functions = {
    "get_current_date": get_current_date,
    "calculate_travel_dates": calculate_travel_dates,
    "get_city_coordinates": get_city_coordinates,
    "get_historical_weather": get_historical_weather
}

# Store conversation histories (in production, use a database)
conversations = {}


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    conversation_id: str


@app.get("/")
async def read_root():
    """Serve the main HTML page"""
    return FileResponse("static/index.html")


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Handle chat requests (non-streaming version)
    For simple request-response without WebSocket
    """
    conversation_id = request.conversation_id or f"conv_{len(conversations)}"
    
    # Get or create conversation history
    if conversation_id not in conversations:
        conversations[conversation_id] = [{
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
        }]
    
    conversation_history = conversations[conversation_id]
    
    # Add user message
    conversation_history.append({
        "role": "user",
        "content": request.message
    })
    
    # Process with OpenAI
    response = await process_chat(conversation_history)
    
    # Add assistant response
    conversation_history.append({
        "role": "assistant",
        "content": response
    })
    
    return ChatResponse(
        response=response,
        conversation_id=conversation_id
    )


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time streaming chat
    """
    await websocket.accept()
    conversation_history = [{
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
    }]
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            if not user_message:
                continue
            
            # Add user message to history
            conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Send acknowledgment
            await websocket.send_json({
                "type": "user_message",
                "content": user_message
            })
            
            # Process with streaming
            await process_chat_streaming(websocket, conversation_history)
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_json({
            "type": "error",
            "content": str(e)
        })


async def process_chat(conversation_history):
    """
    Process chat with OpenAI (non-streaming)
    
    Args:
        conversation_history: List of message dictionaries
    
    Returns:
        str: Final assistant response
    """
    max_iterations = 10
    iteration = 0
    
    # Initial API call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history,
        tools=tools,
        tool_choice="auto"
    )
    
    # Handle tool calls
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
    return final_answer


async def process_chat_streaming(websocket: WebSocket, conversation_history):
    """
    Process chat with OpenAI with streaming support
    
    Args:
        websocket: WebSocket connection
        conversation_history: List of message dictionaries
    """
    max_iterations = 10
    iteration = 0
    
    # Initial API call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history,
        tools=tools,
        tool_choice="auto"
    )
    
    # Handle tool calls
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
            
            # Notify client about tool call
            await websocket.send_json({
                "type": "tool_call",
                "function": function_name,
                "arguments": function_args
            })
            
            # Call the function
            function_response = available_functions[function_name](**function_args)
            
            # Notify client about tool result
            await websocket.send_json({
                "type": "tool_result",
                "function": function_name,
                "result": function_response
            })
            
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
    
    # Stream final answer
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history,
        tools=tools,
        stream=True
    )
    
    full_response = ""
    for chunk in stream:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_response += content
            await websocket.send_json({
                "type": "assistant_stream",
                "content": content
            })
    
    # Send completion signal
    await websocket.send_json({
        "type": "assistant_complete",
        "content": full_response
    })
    
    # Add to history
    conversation_history.append({
        "role": "assistant",
        "content": full_response
    })


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "api_key_set": bool(os.getenv("OPENAI_API_KEY"))}


# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
