import pytest


def test_load_missing_model_does_not_raise():
    """
    Model file may not be present during development or before the first training run.
    The API should start normally and just serve games without predictions.
    """
    import services.model_loader as ml
    ml.load("/nonexistent/path/model.joblib")
    assert ml.predictions_enabled is False


def test_predictions_enabled_after_load(tmp_path, monkeypatch):
    """
    After a successful load, predictions_enabled should be True
    and predict() should return a team ID, probability, and factors list.
    """
    import joblib
    import json
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import FunctionTransformer

    # Build a minimal pipeline that passes data through unchanged
    rf = RandomForestClassifier(n_estimators=10, random_state=42)
    pipe = Pipeline([("passthrough", FunctionTransformer()), ("clf", rf)])

    X = pd.DataFrame({"a": [1, 2, 3, 4], "b": [0, 1, 0, 1]})
    y = [1, 0, 1, 0]
    pipe.fit(X, y)

    model_path = tmp_path / "cfb_ats_model.joblib"
    joblib.dump(pipe, model_path)
    meta = {"columns": ["a", "b"], "top_factors": ["Feature A", "Feature B"]}
    with open(tmp_path / "feature_columns.json", "w") as f:
        json.dump(meta, f)

    import services.model_loader as ml
    ml.predictions_enabled = False
    ml.load(str(model_path))

    assert ml.predictions_enabled is True
    assert ml._feature_columns == ["a", "b"]
    assert ml._top_factors == ["Feature A", "Feature B"]

    row = pd.DataFrame({"a": [2], "b": [1]})
    pick_id, prob, factors = ml.predict(row, home_team_id=1, away_team_id=2)
    assert pick_id in (1, 2)
    assert 0.0 <= prob <= 1.0
    assert len(factors) == 2
