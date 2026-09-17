from pathlib import Path

from src.dl.train import verify_training_dataset


def test_training_dataset_contract():
    contract = verify_training_dataset()
    assert contract["classes"] == ["fire"]
    assert contract["train_images"] == 80
    assert contract["validation_images"] == 10
    assert contract["test_images"] == 10


def test_saved_model_and_metrics_exist_after_training():
    model = Path("models/dl/crime_x_fire_detector.pt")
    metrics = Path("models/dl/model_metrics.json")
    results = Path("models/dl/training_results.csv")
    assert model.is_file()
    assert metrics.is_file()
    assert results.is_file()