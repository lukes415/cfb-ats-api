import joblib
import json
import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

# Module-level state loaded once at startup.
# Keeping these at module scope means we load the ~50MB model file once,
# not on every prediction request.
_model = None
_feature_columns: list[str] = []
_top_factors: list[str] = []
predictions_enabled: bool = False


def load(model_path: str) -> None:
    """
    Load the trained sklearn Pipeline and feature metadata.
    Called once via FastAPI's lifespan event — never per-request.

    If the model file is absent, predictions_enabled stays False and the
    endpoint omits prediction fields. This lets the API boot
    without a trained model during development or after a failed training run.
    """
    global _model, _feature_columns, _top_factors, predictions_enabled

    path = Path(model_path)
    if not path.exists():
        logger.warning(f"No model at {model_path} — predictions disabled")
        return

    _model = joblib.load(path)

    # feature_columns.json lives next to the model file.
    # Column order must exactly match training.
    columns_path = path.parent / "feature_columns.json"
    with open(columns_path) as f:
        meta = json.load(f)

    _feature_columns = meta["columns"]

    # top_factors are global (computed from feature_importances_ at training time),
    # not per-game. We chose this over SHAP (for now) because it's free to compute,
    # requires no additional library, and is honest: these ARE what the model weights most.
    _top_factors = meta["top_factors"]

    predictions_enabled = True
    logger.info(f"Loaded {len(_feature_columns)}-feature pipeline from {model_path}")


def predict(feature_df: pd.DataFrame, home_team_id: int, away_team_id: int) -> tuple[int, float, list[str]]:
    """
    Run inference on a single-game feature row.

    The model predicts whether the HOME team covers (class 1 = home covers).
    If prob >= 0.5 we pick the home team; otherwise the away team and flip
    the probability so it always represents confidence in the actual pick.

    Returns:
        (model_pick_team_id, prob_cover, top_factors)
    """
    proba = _model.predict_proba(feature_df[_feature_columns])[0]

    # classes_ order is not guaranteed — find index of class 1 explicitly
    cover_idx = list(_model.classes_).index(1)
    prob_home_covers = float(proba[cover_idx])

    if prob_home_covers >= 0.5:
        return home_team_id, prob_home_covers, _top_factors
    else:
        # Flip so prob_cover always represents the picked team's likelihood
        return away_team_id, 1.0 - prob_home_covers, _top_factors
