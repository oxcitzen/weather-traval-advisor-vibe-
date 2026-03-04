"""
Interactive CLI for Travel Weather Planner
Run this for a conversational interface.
"""

import os
from dotenv import load_dotenv
from weather_planner import chat_with_travel_planner

# Load environment variables
load_dotenv()

def main():
    """Interactive chat loop"""
    print("=" * 60)
    print("🌍 TRAVEL WEATHER PLANNER - Interactive Mode")
    print("=" * 60)
    print("\nAsk me about weather for your upcoming travel!")
    print("Examples:")
    print("  - 'I'm planning a trip to Tokyo for next month'")
    print("  - 'What's the weather like in Paris in 2 weeks?'")
    print("  - 'Should I bring an umbrella to London next month?'")
    print("\nType 'quit' or 'exit' to end the conversation.\n")
    
    conversation_history = None
    
    while True:
        # Get user input
        user_input = input("You: ").strip()
        
        # Check for exit commands
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("\n👋 Safe travels! Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Get response
        try:
            response, conversation_history = chat_with_travel_planner(
                user_input, 
                conversation_history
            )
            print(f"\n🤖 Assistant: {response}\n")
            print("-" * 60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
            print("Please check your .env file and API key.\n")
            break

if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in .env file")
        print("\n📝 Setup instructions:")
        print("1. Copy .env.example to .env")
        print("2. Add your OpenAI API key to .env")
        print("3. Run this script again")
    else:
        main()