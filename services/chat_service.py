from openai import OpenAI
from config import settings
import json
from pathlib import Path

client = OpenAI(api_key=settings.openai_api_key)
sample_size = 15

class ChatService:

    def __init__(self):
        self._teams = self._load_teams()

    def _load_teams(self) -> list:
        """Load teams reference data"""
        teams_file = Path("reference_data/all_teams.json")
        try:
            with open(teams_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {teams_file} not found")
            return []

    def _normalize_team_name(self, query_text: str) -> str:
        """
        Find official team name from query text using school name, team nickname, or alternate names.
        Returns official "school" name or None if not found.
        Note that this logic is rudimentary for now. Schools with a space in their name will likely not be found,
        e.g. Florida State will return Florida because of short circuiting.
        """
        query_lower = query_text.lower()
        
        for team in self._teams:
            # Check school name
            if team.get("school", "").lower() in query_lower:
                return team["school"]
            
            # Check mascot
            if team.get("mascot", "").lower() in query_lower:
                return team["school"]
            
            # Check abbreviation
            if team.get("abbreviation", "").lower() in query_lower:
                return team["school"]
            
            # Check alternate names
            alt_names = team.get("alternateNames")
            for alt in alt_names:
                if alt and alt.lower() in query_lower:
                    return team["school"]
        
        return None


    def _detect_team_in_question(self, question: str, games_data: list) -> str:
        team = self._normalize_team_name(question)
        return team

    def _filter_games_by_team(self, games_data: list, team: str) -> list:
        """Filter games to only those involving specified team"""
        return [
            g for g in games_data 
            if g.get("homeTeam") == team or g.get("awayTeam") == team
        ]

    def _prepare_game_data(self, question: str, games_data: list) -> dict:
        """
        Prepare and filter game data based on the question.
        Returns: {
            "data": filtered or sampled games,
            "team_filter": team name or None,
            "context_note": description of what data is being used
        }
        """
        team = self._detect_team_in_question(question, games_data)
        
        if team:
            print("hello")
            relevant_data = self._filter_games_by_team(games_data, team)
            context_note = f"Filtered to {len(relevant_data)} games involving {team}"
        else:
            relevant_data = games_data[:20]  # Sample for general questions
            context_note = f"Using sample of {len(relevant_data)} games from {len(games_data)} total"
        
        return {
            "data": relevant_data,
            "team_filter": team,
            "context_note": context_note
        }
    def _build_system_message(self, prepared_data: dict, games_data: list) -> str:
        """Build the system message for the LLM"""
        available_fields = list(prepared_data["data"][0].keys()) if prepared_data["data"] else []
        
        return f"""You are a college football analytics assistant.

                Dataset: {prepared_data["context_note"]}

                Available fields: {", ".join(available_fields)}

                Instructions:
                - Answer based ONLY on the provided game data
                - Be specific with numbers and statistics
                - If you can"t find the answer in the data, say so clearly
                - Focus on facts from the data, not general football knowledge"""

    async def answer_question(self, question: str, games_data: list = None):
        """
        Use GPT to answer questions about CFB data
        """
        if not games_data:
            return {
                "answer": "There is no game data available to analyze.",
                "tokens_used": 0
            }
        prepared = self._prepare_game_data(question, games_data)
        messages = [
            {
                "role": "system", 
                "content": self._build_system_message(prepared, games_data)
            },
            {
                "role": "system", 
                "content": f"Game data:\n{json.dumps(prepared['data'], indent=2)}"
            },
            {
                "role": "user",
                "content": question
            }
        ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2,
            max_tokens=400
        )
        
        return {
            "answer": response.choices[0].message.content,
            # "tokens_used": response.usage.total_tokens, 
            # "games_analyzed": len(prepared["data"]),
            # "team_filter": prepared["team_filter"]
        }

chat_service = ChatService()