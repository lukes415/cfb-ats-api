from fastapi import APIRouter, Query
from .deps import get_model_bundle  # loads model + featurizer
router = APIRouter()

@router.get("/")
def predict(season: int = Query(...), week: int = Query(...)):
    model, featurizer = get_model_bundle()
    X, meta = featurizer.build_matrix(season=season, week=week)  # pulls cached CFBD data
    proba = model.predict_proba(X)[:,1]
    picks = (proba >= 0.5).astype(int).tolist()
    return [
        {
          "game_id": m["game_id"],
          "home_team_id": m["home_team_id"],
          "away_team_id": m["away_team_id"],
          "spread": m["spread"],
          "prob_cover": float(p),
          "model_pick": bool(p >= 0.5)
        }
        for p, m in zip(proba, meta)
    ]
