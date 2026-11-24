import unittest
from unittest.mock import patch, Mock

from scripts.api_contract_validator import (
    validate_openapi,
    fetch_openapi,
)


def valid_document():
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "InfraSentry AI",
            "version": "1.0.0",
        },
        "paths": {
            "/health": {
                "get": {
                    "operationId": "health_check",
                    "responses": {
                        "200": {"description": "Healthy"}
                    },
                }
            }
        },
    }


class APIContractTests(unittest.TestCase):

    def test_valid_contract(self):
        self.assertEqual(validate_openapi(valid_document()), [])

    def test_missing_api_title(self):
        document = valid_document()
        document["info"]["title"] = ""

        errors = validate_openapi(document)

        self.assertTrue(any("API title" in error for error in errors))

    def test_missing_paths(self):
        document = valid_document()
        document["paths"] = {}

        errors = validate_openapi(document)

        self.assertTrue(any("No API paths" in error for error in errors))

    def test_missing_responses(self):
        document = valid_document()
        document["paths"]["/health"]["get"]["responses"] = {}

        errors = validate_openapi(document)

        self.assertTrue(any("Missing responses" in error for error in errors))

    def test_duplicate_operation_ids(self):
        document = valid_document()
        document["paths"]["/status"] = {
            "get": {
                "operationId": "health_check",
                "responses": {"200": {"description": "OK"}},
            }
        }

        errors = validate_openapi(document)

        self.assertTrue(any("Duplicate operationId" in error for error in errors))

    def test_invalid_openapi_version(self):
        document = valid_document()
        document["openapi"] = "2.0"

        errors = validate_openapi(document)

        self.assertTrue(any("OpenAPI 3.x" in error for error in errors))

    @patch("scripts.api_contract_validator.urlopen")
    def test_fetch_openapi(self, mock_urlopen):
        response = Mock()
        response.status = 200
        response.read.return_value = b'{"openapi":"3.1.0"}'
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = response

        result = fetch_openapi("http://localhost/openapi.json")

        self.assertEqual(result["openapi"], "3.1.0")


if __name__ == "__main__":
    unittest.main()
