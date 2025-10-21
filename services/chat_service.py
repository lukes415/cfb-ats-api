from openai import OpenAI
from config import settings
import json

client = OpenAI(api_key=settings.openai_api_key)

class ChatService:
    def test(self):
        return {"answer": "hi"}
    
    async def answer_question(self, question: str, games_data: list = None):
        """
        Use GPT to answer questions about CFB data
        """
        messages = [
            {
                "role": "system", 
                "content": "You are a highly skilled data analyst with deep college football domain expertise. Answer questions about games, teams, and statistics based on the provided data."
            },
            {"role": "user", "content": question}
        ]
        
        # If we have data to analyze, include it
        if games_data:
            messages.insert(1, {
                "role": "system",
                "content": f"Here is the relevant game data: {json.dumps(games_data[:15])}"  # Limit to avoid token limits
            })
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return {
            "answer": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens
        }

chat_service = ChatService()