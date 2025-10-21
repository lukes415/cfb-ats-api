from openai import OpenAI
from config import settings
import json

client = OpenAI(api_key=settings.openai_api_key)
sample_size = 15

class ChatService:
    
    async def answer_question(self, question: str, games_data: list = None):
        """
        Use GPT to answer questions about CFB data
        """
        messages = [
            {
                "role": "system", 
                "content": f"You are a highly skilled data analyst with deep college football domain expertise. The user has asked about data from college football games. There are {len(games_data) if games_data else 0} games in the dataset provided."
            },
            {
                "role": "system",
                "content": f"Here is a sample of {sample_size} games to understand the data structure: {json.dumps(games_data[:sample_size], indent=2) if games_data else []}"
            },
            {"role": "user", "content": question}
        ]
        
        # If we have data to analyze, include it
        if games_data:
            messages.insert(1, {
                "role": "system",
                "content": f"Here is the relevant game data: {json.dumps(games_data[:sample_size])}"  # Limit to avoid token limits
            })
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            max_tokens=500
        )
        
        return {
            "answer": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens
        }

chat_service = ChatService()