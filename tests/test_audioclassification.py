# Tests for the audioclassification module

# Tests for the audioclassification module

import pytest
import torch
import numpy as np
from unittest.mock import patch, MagicMock
from audioclassification import AudioClassifier

# Constants for testing
N_MFCC = 26
NUM_EPOCHS = 3
BATCH_SIZE = 32
SAMPLE_DATA_SIZE = 100
MODELS_PATH = 'models'  # Mock models path


@pytest.fixture
def audio_classifier():
    """
    Fixture to create an instance of AudioClassifier with a mocked models path.
    """
    return AudioClassifier(N_MFCC, MODELS_PATH)


def test_audio_classifier_initialization(audio_classifier):
    """
    Test the initialization of the AudioClassifier class to ensure it is instantiated correctly.
    """
    assert isinstance(audio_classifier, AudioClassifier), "AudioClassifier should be correctly instantiated"
    assert audio_classifier.models_path == MODELS_PATH, "Models path should be correctly set"


@patch('audioclassification.torch.save')
@patch('joblib.dump')
def test_new_model_training(mock_dump, mock_save, audio_classifier):
    """
    Test the new_model method of the AudioClassifier class for training a new model.
    This includes testing the model training process and saving of the model.
    """
    # Generating mock features and labels for binary classification
    mock_features_positive = np.random.rand(SAMPLE_DATA_SIZE // 2, N_MFCC)
    mock_labels_positive = np.ones(SAMPLE_DATA_SIZE // 2)  # All 1s
    mock_features_negative = np.random.rand(SAMPLE_DATA_SIZE // 2, N_MFCC)
    mock_labels_negative = np.zeros(SAMPLE_DATA_SIZE // 2)  # All 0s

    # Call the new_model method with mock data
    audio_classifier.new_model(mock_features_positive, mock_features_negative,
                               mock_labels_positive, mock_labels_negative,
                               num_epochs=NUM_EPOCHS, verbose=True, save_scaler=False)

    # Assertions to verify training and saving
    assert audio_classifier.scaler is not None, "Scaler should be initialized"
    mock_save.assert_called()  # Check if model is saved after training
    mock_dump.assert_not_called()  # Ensure scaler is not saved after test with mock data


def test_load_model(audio_classifier):
    """
    Test the load_model method of the AudioClassifier class.
    This test verifies that the model and scaler are correctly loaded.
    """
    model_name = 'model_v1.pth'

    # Create a mock state dictionary
    mock_state_dict = {
        'fc1.weight': torch.rand(128, N_MFCC),
        'fc1.bias': torch.rand(128),
        'fc2.weight': torch.rand(64, 128),
        'fc2.bias': torch.rand(64),
        'fc3.weight': torch.rand(2, 64),
        'fc3.bias': torch.rand(2)
    }

    # Mock torch.load to return the mock state dictionary
    with patch('torch.load', return_value=mock_state_dict):
        audio_classifier.load_model(model_name, verbose=True)

        # Assertions to verify model loading
        assert audio_classifier.scaler is not None, "Scaler should be loaded with the model"


def test_model_evaluation(audio_classifier):
    """
    Test the model evaluation (forward pass) of the AudioClassifier class.
    This test ensures that the model can process input data and produce output correctly.
    """
    # Create a mock input tensor
    mock_input = torch.rand(BATCH_SIZE, N_MFCC)

    # Perform a forward pass
    with torch.no_grad():
        output = audio_classifier(mock_input)

    # Assertions to verify the forward pass
    assert output.shape[0] == BATCH_SIZE, "Output batch size should match input"
    assert output.shape[1] == 2, "Output should have 2 nodes (binary classification)"
