from pathlib import Path

import pytest

from src.services.crime_service import get_crime_overview, get_district_ranking, get_state_ranking
from src.services.crime_x_service import CrimeXService
from src.services.cybercrime_service import get_cybercrime_categories, get_cybercrime_overview, get_fraud_analysis
from src.services.fire_detection_service import detect_fire
from src.services.prediction_service import predict_crime_count


TEST_IMAGE = next(Path("data/processed/dl_yolo/images/test").glob("*.jpg"))


def test_crime_service_returns_jsonable_results():
    overview = get_crime_overview()
    assert overview["total_crime"] > 0
    assert isinstance(get_state_ranking(3), list)
    assert isinstance(get_district_ranking(3), list)
    assert "source" not in overview


def test_cybercrime_services_return_records():
    overview = get_cybercrime_overview()
    assert overview["total_cyber_crimes"] > 0
    assert isinstance(get_cybercrime_categories(), list)
    assert isinstance(get_fraud_analysis(), list)


def test_prediction_service_returns_contract():
    result = predict_crime_count({
        "lag_2020_count": 100,
        "lag_2021_count": 90,
        "population_2022_lakhs": 500,
    })
    assert result["module"] == "crime_prediction"
    assert result["confidence"] is None
    assert "warning" in result


def test_fire_detection_service_returns_contract():
    result = detect_fire(TEST_IMAGE)
    assert result["module"] == "fire_detection"
    assert result["image_width"] > 0
    assert result["image_height"] > 0
    assert isinstance(result["detections"], list)


def test_unified_facade_exposes_all_modules():
    service = CrimeXService()
    assert service.get_crime_overview()["total_crime"] > 0
    assert service.get_cybercrime_overview()["total_cyber_crimes"] > 0
    assert service.predict_crime_count({
        "lag_2020_count": 100,
        "lag_2021_count": 90,
        "population_2022_lakhs": 500,
    })["module"] == "crime_prediction"


def test_service_input_errors_are_explicit():
    with pytest.raises(ValueError):
        predict_crime_count({"lag_2020_count": 1})
    with pytest.raises(ValueError):
        detect_fire("data/processed/dl_yolo/images/test/not-supported.gif")