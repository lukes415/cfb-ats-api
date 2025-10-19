# CFB ATS API
Service to expose ATS model predictions for college football games

## Testing
Run the app with `uvicorn app.main:app --reload`

## Status
Adding in an endpoint to retrieve game data asynchronously. Stubbing other data to pull from CFBD. These endpoints will be used to pull data to build the model's dataset

## Completed
- [x] Scaffolding
- [x] Hooked up /games to pull from CFBD
- [x] Added live and health checks
- [x] Created endpoint stubs for teams, coaches, venues, lines, weather, score, and predict

## Next Steps
 - [x] Create mock endpoints
 - [ ] Create an endpoint that pulls from a real model
 - [ ] Build and expose specs

## Future Goals
- [ ] Build and expose an endpoint to get weekly picks from the model and data from CFBD
- [ ] Allow a user to retrieve games, teams, weather, lines, coaches, etc.
- [ ] Allow a user to retrieve picks for specific teams of interests
- [ ] Stretch: Allow support for retrieving realtime game information to support push notifications

## Tech
- FastAPI and Pydantic (pending)
- skl or xgboost model loader
- Docker / similar
- Github Actions CI/CD

