# CFB ATS API
Service to expose ATS model predictions for college football games

## Testing
Run the app with
`uvicorn main:app --reload`

 ## Chatbot Progress
 I updated the chatbot to use function calling to support additional types of queries in the future. I also updated the team matching logic to properly identify "Florida State" instead of "Florida"

 **Example**
 ```bash
 POST /v1/chat
 {
    "question": "How many games did the Florida State play in 2024?"
    "year": 2024
 }
```

**Response**
```json
{
    "answer": "Florida State played 12 games in the 2024 season.",
    "tokens_used": 3984,
    "function_called": "get_team_games",
    "function_args": {
        "team_name": "Florida State"
    },
    "matched_team_from_dataset": "Florida State"
}
```
![Chat API Example](screenshots/games_function_call.png)

## Completed 
 - [x] Add live connectivity to games, coaches, lines, teams, venues, and weather endpoints
 - [x] Build a local caching mechanism to reduce calls to CFBD
- [x] Introduce a natural language endpoint powered by OpenAI to answer questions about the dataset
- [x] Use Pydantic for configuration management and data validations
- [x] Updated the natural language endpoint to use function calling
- [x] Integrate the ATS picks ML model (`cfb-ats-data` Pipeline loaded via `model_loader.py`, features assembled by `featurizer.py`)
- [x] Allow a user to retrieve picks for specific teams of interest

## `GET /v1/teams/next-game`
Returns the next upcoming game for each requested team, enriched with venue, weather, consensus spread, and the model's ATS prediction.

```bash
GET /v1/teams/next-game?team_ids=57,2579
```

If the model file hasn't been loaded, the `prediction` field is omitted but the rest of the response still works.

## Next Steps
- [ ] Add additional functions to the chat endpoint
- [ ] Build out logging and expose specs
- [ ] Docker / similar
- [ ] Github Actions CI/CD
- [ ] Stretch: Allow support for retrieving realtime game information to support push notifications

## Tech
- FastAPI and Pydantic
- OpenAI GPT-4 for natural language interface
- scikit-learn Pipeline (TargetEncoder + RandomForest) loaded via joblib
- Async HTTP requests using httpx
- File-based caching

