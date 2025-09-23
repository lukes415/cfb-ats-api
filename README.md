# CFB ATS API
Service to expose ATS model predictions for college football games

## Status
Work in progress. Focusing on the feature engineering and the model right now.

## Goals
- [ ] Build and expose an endpoint to get weekly picks from the model
- [ ] Allow a user to retrieve all teams, and relevant details
- [ ] Allow a user to retrieve picks for specific teams of interests
- [ ] Stretch: Allow support for retrieving realtime game information to support push notifications

## Tech
- FastAPI and Pydantic
- skl or xgboost model loader
- Docker / similar
- Github Actions CI/CD

## Next Steps
 - [ ] Create mock endpoints
 - [ ] Create an endpoint that pulls from a real model
 - [ ] Build and expose specs

