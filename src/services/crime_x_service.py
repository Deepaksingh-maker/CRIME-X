"""Unified backend facade for completed CRIME X intelligence modules."""

from __future__ import annotations

from .crime_service import get_crime_overview, get_district_ranking, get_state_ranking
from .cybercrime_service import get_cybercrime_categories, get_cybercrime_overview, get_fraud_analysis
from .fire_detection_service import detect_fire
from .prediction_service import predict_crime_count


class CrimeXService:
    """Single application-facing facade for analytics, prediction, and detection."""

    get_crime_overview = staticmethod(get_crime_overview)
    get_state_ranking = staticmethod(get_state_ranking)
    get_district_ranking = staticmethod(get_district_ranking)
    get_cybercrime_overview = staticmethod(get_cybercrime_overview)
    get_cybercrime_categories = staticmethod(get_cybercrime_categories)
    get_fraud_analysis = staticmethod(get_fraud_analysis)
    predict_crime_count = staticmethod(predict_crime_count)
    detect_fire = staticmethod(detect_fire)