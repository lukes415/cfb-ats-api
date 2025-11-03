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
        Updated logic to find the team with the longest name that matches the query to resolve Florida vs. Florida State issue
        """
        query_lower = query_text.lower()
        matches = []
        
        for team in self._teams:
            school = team.get("school", "")
            abbrev = team.get("abbreviation", "")
            alt_names = team.get("alternativeNames", "")
            all_names = [school] + [abbrev] + [a for a in alt_names if a]

            for name in all_names:
                if name and name.lower() in query_lower:
                    matches.append((len(name), team["school"], name))
        
        if matches:
            # The values will be sorted by the length of the name
            matches.sort(reverse = True)
            # Return the first (longest) school name in the matches set
            return matches[0][1]
        
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
        # Team filter function, will be extended with additional functions
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_team_games",
                    "description": "Get all games for a specific college football team. Use this when the user asks about a specific team's games, performance, or statistics.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "team_name": {
                                "type": "string",
                                "description": "The name of the college football team (e.g., 'Alabama', 'Florida State', 'Ohio State'). Can be full name, abbreviation, or nickname."
                            }
                        },
                        "required": ["team_name"]
                    }
                }
            }
        ]
        messages = [
            {
                "role": "system",
                "content": f"You are a college football analytics assistant with access to {len(games_data)} games. When asked about a specific team, use the get_team_games function to retrieve relevant data."
            },
            {"role": "user", "content": question}
        ]
        
        # First API call - LLM decides if it needs to call function
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        # If LLM wants to call the function
        if tool_calls:
            # Add LLM's response to messages
            messages.append(response_message)
            
            # Process each tool call (usually just one)
            for tool_call in tool_calls:
                print("tool call: ", tool_call)
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"LLM calling function: {function_name} with args: {function_args}")
                
                if function_name == "get_team_games":
                    # Use existing team name normalization
                    team_name = function_args.get("team_name", "")
                    normalized_team = self._normalize_team_name(team_name)

                    # print("normalized team: ", normalized_team)
                    
                    if normalized_team:
                        # Filter games for this team
                        filtered_games = [
                            g for g in games_data 
                            if g.get('homeTeam') == normalized_team or g.get('awayTeam') == normalized_team
                        ]
                        function_result = {
                            "team": normalized_team,
                            "games_found": len(filtered_games),
                            "games": filtered_games
                        }
                    else:
                        function_result = {
                            "error": f"Could not find team: {team_name}",
                            "games_found": 0,
                            "games": []
                        }
                else:
                    function_result = {"error": "Unknown function"}
                
                # Add function result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(function_result)
                })
            
            # Second API call - LLM uses the function results to answer
            second_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            # Added the matched_team_from_dataset to validate that the requested team was properly identified by the internal logic before passing to the LLM
            return {
                "answer": second_response.choices[0].message.content,
                "tokens_used": response.usage.total_tokens + second_response.usage.total_tokens,
                "function_called": function_name,
                "function_args": function_args,
                "matched_team_from_dataset": normalized_team
            }
        
        # No function call needed - LLM answered directly
        return {
            "answer": response_message.content,
            "tokens_used": response.usage.total_tokens
        }
chat_service = ChatService()