import json

import pytest
from unittest.mock import Mock, patch

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),"../../../python/lambdas"))

from python.lambdas.ingestion.get_venues import lambda_handler


# Mock response from requests.get
@pytest.fixture
def mock_response():
    return json.load(open(f"tests/unit/fixtures/all_venues.json", "r"))["sections"][1]["items"]


@pytest.fixture
def mock_event_context():
    return {}, Mock()


@pytest.fixture
def mock_wolt():
    with patch('python.lambdas.ingestion.get_venues.Wolt') as mock_wolt:
        yield mock_wolt


@pytest.fixture
def mock_search():
    with patch('python.lambdas.ingestion.get_venues.Search') as mock_search:
        yield mock_search


@pytest.fixture
def mock_storage():
    with patch('python.lambdas.ingestion.get_venues.Storage') as mock_storage:
        yield mock_storage


# Test function
def test_lambda_handler(mock_response, mock_event_context, mock_search, mock_storage, mock_wolt):
    mock_wolt.return_value.get_venues.return_value = mock_response
    mock_storage.return_value.save_raw_venue.return_value = None
    mock_search.return_value.indexed_venues.return_value = []

    # Call the function with the mock event and context
    response = lambda_handler(*mock_event_context)

    # Assert the body contains the expected venues
    assert response["Payload"] == [
        {"s": "tasty"},
        {"s": "begheli1"},
        {"s": "premium-sandwich"}
    ]


def test_lambda_handler_fully_ingested(mock_response, mock_event_context, mock_search, mock_storage, mock_wolt):
    mock_wolt.return_value.get_venues.return_value = mock_response
    mock_storage.return_value.save_raw_venue.return_value = None
    mock_search.return_value.indexed_venues.return_value = ["tasty", "begheli1", "premium-sandwich"]

    # Call the function with the mock event and context
    response = lambda_handler(*mock_event_context)

    # Assert the body contains the expected venues
    assert response["Payload"] == []


def test_lambda_handler_partially_ingested(mock_response, mock_event_context, mock_search, mock_storage, mock_wolt):
    mock_wolt.return_value.get_venues.return_value = mock_response
    mock_storage.return_value.save_raw_venue.return_value = None
    mock_search.return_value.indexed_venues.return_value = ["tasty", "premium-sandwich"]

    # Call the function with the mock event and context
    response = lambda_handler(*mock_event_context)

    # Assert the body contains the expected venues
    assert response["Payload"] == [{"s": "begheli1"}]


def test_lambda_handler_fully_ingested_refresh(mock_response, mock_event_context, mock_search, mock_storage, mock_wolt):
    mock_wolt.return_value.get_venues.return_value = mock_response
    mock_storage.return_value.save_raw_venue.return_value = None
    mock_search.return_value.indexed_venues.return_value = ["tasty", "begheli1", "premium-sandwich"]

    # Call the function with the mock event and context
    response = lambda_handler({"refresh": True}, Mock())

    # Assert the body contains the expected venues
    assert response["Payload"] == [
        {"s": "tasty"},
        {"s": "begheli1"},
        {"s": "premium-sandwich"}
    ]