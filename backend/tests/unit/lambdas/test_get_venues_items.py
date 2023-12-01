import json

import pytest
from unittest.mock import MagicMock, patch

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)),"../../../python/lambdas"))

from python.lambdas.get_venue_items import lambda_handler


@pytest.fixture
def single_venue_response():
    return {"Body": open("tests/unit/fixtures/single_venue.json", "rb")}


@pytest.fixture
def venue_categories_response():
    return json.load(open("tests/unit/fixtures/venue_categories.json", "r"))


@pytest.fixture
def venue_category_menu_response():
    return json.load(open("tests/unit/fixtures/venue_category_items.json", "r"))


@pytest.fixture
def mock_requests_get():
    with patch('get_venue_items.requests.get') as mock_get:
        yield mock_get


@pytest.fixture
def mock_boto3_client():
    with patch('get_venue_items.boto3.client') as mock_boto3:
        yield mock_boto3


@pytest.fixture
def mock_os_getenv():
    with patch('os.getenv') as mock_getenv:
        yield mock_getenv


def test_lambda_handler_with_valid_event(
    mock_requests_get,
    mock_boto3_client,
    mock_os_getenv,
    single_venue_response,
    venue_categories_response,
    venue_category_menu_response
):
    # Mocking the os.getenv calls
    mock_os_getenv.return_value = "test_value"

    # Mocking the boto3 client
    s3_client_mock = MagicMock()
    s3_client_mock.get_object.return_value = single_venue_response
    mock_boto3_client.return_value = s3_client_mock

    # Mocking the requests.get calls
    mock_response = MagicMock()
    mock_response.json.side_effect = [
        venue_categories_response,
        *[
            venue_category_menu_response
            for _ in range(len(venue_categories_response["categories"]))
        ]
    ]
    mock_requests_get.return_value = mock_response

    # Mocking the event
    event = {"s": "test_slug"}

    # Calling the function
    lambda_handler(event, "context")

    # Assertions
    mock_os_getenv.assert_called()
    mock_boto3_client.assert_called_with('s3')
    mock_requests_get.assert_called()
    s3_client_mock.put_object.assert_called()


def test_lambda_handler_with_invalid_event(mock_requests_get, mock_boto3_client, mock_os_getenv):
    # Mocking the os.getenv calls
    mock_os_getenv.return_value = "test_value"

    # Mocking the event
    event = {"invalid_key": "test_slug"}

    # Calling the function
    with pytest.raises(KeyError):
        lambda_handler(event, "context")

    # Assertions
    mock_os_getenv.assert_called()
    mock_boto3_client.assert_called_with('s3')
    mock_requests_get.assert_not_called()

def test_lambda_handler_request_fail(
        mock_requests_get,
        mock_boto3_client,
        mock_os_getenv,
        single_venue_response
    ):
    # Mocking the os.getenv calls
    mock_os_getenv.return_value = "test_value"

    # Mocking the boto3 client
    s3_client_mock = MagicMock()
    s3_client_mock.get_object.return_value = single_venue_response
    mock_boto3_client.return_value = s3_client_mock

    # Mocking the requests.get to raise an exception
    mock_requests_get.side_effect = Exception("Failed to fetch data")

    # Mocking the event
    event = {"s": "test_slug"}

    # Calling the function
    with pytest.raises(Exception):
        lambda_handler(event, "context")

    # Assertions
    mock_os_getenv.assert_called()
    mock_boto3_client.assert_called_with('s3')
    mock_requests_get.assert_called()
    s3_client_mock.put_object.assert_not_called()


def test_lambda_handler_s3_fail(
        mock_requests_get,
        mock_boto3_client,
        mock_os_getenv,
        single_venue_response,
        venue_categories_response,
        venue_category_menu_response
    ):
    # Mocking the os.getenv calls
    mock_os_getenv.return_value = "test_value"

    # Mocking the boto3 client
    s3_client_mock = MagicMock()
    s3_client_mock.get_object.return_value = single_venue_response
    s3_client_mock.put_object.side_effect = Exception("Failed to put object")
    mock_boto3_client.return_value = s3_client_mock

    # Mocking the requests.get calls
    mock_response = MagicMock()
    mock_response.json.side_effect = [
        venue_categories_response,
        *[
            venue_category_menu_response
            for _ in range(len(venue_categories_response["categories"]))
        ]
    ]
    mock_requests_get.return_value = mock_response

    # Mocking the event
    event = {"s": "test_slug"}

    # Calling the function
    with pytest.raises(Exception):
        lambda_handler(event, "context")

    # Assertions
    mock_os_getenv.assert_called()
    mock_boto3_client.assert_called_with('s3')
    mock_requests_get.assert_called()
    s3_client_mock.put_object.assert_called()