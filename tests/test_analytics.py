import pandas as pd

from services.analytics_service import get_cybercrime_analysis, get_gujarat_analysis
from src.data.analysis import CYBER_TOTAL_COLUMN, physical_crime_analysis, state_ranking
from src.data.loader import load_csv


def test_cybercrime_analysis_uses_real_rows_and_categories():
    result = get_cybercrime_analysis()
    assert result["total_cyber_crimes"] == 65893
    assert len(result["state_ranking"]) == 10
    assert "category" in result["category_distribution"].columns
    assert "fraud_distribution" in result


def test_gujarat_analysis_has_actual_chronological_years():
    result = get_gujarat_analysis()
    yearly = result["yearly"]
    assert yearly["year"].tolist() == [2014, 2015, 2016, 2017, 2018]
    assert yearly.iloc[0]["total_cases"] == 8733
    assert pd.isna(yearly.iloc[0]["year_over_year_change"])


def test_physical_snapshot_supports_state_and_district_rankings():
    dataframe = load_csv("data/ncrb 2022/data/NCRB_District_Table_1.1.csv")
    result = physical_crime_analysis(dataframe)
    assert result["is_time_series"] is False
    assert len(result["state_ranking"]) == 10
    assert result["state_ranking"].iloc[0]["state_ut"] != "Total Districts"
    assert result["total_crime"] < dataframe["Total Cognizable IPC crimes - Col. ( 144)"].sum()


def test_state_ranking_sorts_descending():
    dataframe = pd.DataFrame({"state_ut": ["A", "B", "A"], CYBER_TOTAL_COLUMN: [2, 5, 3]})
    result = state_ranking(dataframe, CYBER_TOTAL_COLUMN, limit=2)
    assert result.iloc[0].to_dict() == {"state_ut": "A", "total_cases": 5}