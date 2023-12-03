import json

import pytest
from unittest.mock import MagicMock, patch, Mock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),"../../../python/lambdas"))

from python.lambdas.process_venue_items import lambda_handler


@pytest.fixture
def single_venue_response():
    return json.load(open("tests/unit/fixtures/single_venue.json", "r"))


@pytest.fixture
def venue_categories_response():
    return json.load(open("tests/unit/fixtures/venue_categories.json", "r"))["categories"]


@pytest.fixture
def category_items_response():
    return json.load(open("tests/unit/fixtures/venue_category_items.json", "r"))["items"]


@pytest.fixture
def mock_event_context():
    return {"s": "test-venue"}, Mock()


@pytest.fixture
def mock_wolt():
    with patch('python.lambdas.process_venue_items.Wolt') as mock_wolt:
        yield mock_wolt


@pytest.fixture
def mock_storage():
    with patch('python.lambdas.process_venue_items.Storage') as mock_storage:
        yield mock_storage


def test_lambda_handler_with_valid_event(
    mock_event_context,
    mock_storage,
    mock_wolt,
    single_venue_response,
    venue_categories_response,
    category_items_response
):
    mock_storage.return_value.get_raw_venue.return_value = single_venue_response
    mock_wolt.return_value.categories.return_value = venue_categories_response
    mock_wolt.return_value.menu_items.return_value = category_items_response

    response = lambda_handler(*mock_event_context)
    assert response == mock_event_context[0]
