import json

import pytest
from unittest.mock import Mock
from python.lambdas.get_venues import lambda_handler

# Mock response from requests.get
@pytest.fixture
def mock_response():
    return json.load(open("tests/unit/fixtures/get_venues_response.json", "r"))

# Mock event and context
@pytest.fixture
def mock_event_context():
    return {}, Mock()

# Test function
def test_lambda_handler(mock_response, mock_event_context, mocker):
    # Mock requests.get
    mocker.patch("requests.get", return_value=Mock(json=lambda: mock_response))

    # Mock boto3.client
    s3_client_mock = mocker.patch("boto3.client")
    s3_client_mock.return_value.put_object.return_value = {}

    # Call the function with the mock event and context
    response = lambda_handler(*mock_event_context)

    # Assert the status code is 200
    assert response["statusCode"] == 200

    # Assert the body contains the expected venues
    assert response["Payload"] == [
        {"s": "tasty"},
        {"s": "begheli1"},
        {"s": "premium-sandwich"}
    ]

def test_lambda_handler_request_fail(mock_event_context, mocker):
    # Mock requests.get to raise an exception
    mocker.patch("requests.get", side_effect=Exception("Failed to fetch data"))

    # Call the function with the mock event and context
    response = lambda_handler(*mock_event_context)

    # Assert the status code is 500
    assert response["statusCode"] == 500

def test_lambda_handler_s3_fail(mock_response, mock_event_context, mocker):
    # Mock requests.get
    mocker.patch("requests.get", return_value=Mock(json=lambda: mock_response))

    # Mock boto3.client to raise an exception
    s3_client_mock = mocker.patch("boto3.client")
    s3_client_mock.return_value.put_object.side_effect = Exception("Failed to put object")

    # Call the function with the mock event and context
    response = lambda_handler(*mock_event_context)

    # Assert the status code is 500
    assert response["statusCode"] == 500

def test_lambda_handler_no_venues(mock_event_context, mocker):
    # Mock requests.get to return no venues
    mocker.patch("requests.get", return_value=Mock(json=lambda: {"sections": [{}, {}]}))

    # Call the function with the mock event and context
    response = lambda_handler(*mock_event_context)

    # Assert the status code is 200 and the body is an empty list
    assert response["statusCode"] == 500
    assert "KeyError" in response["body"]["message"]
