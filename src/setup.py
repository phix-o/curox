import fastapi.openapi.utils as openapi_utils
import fastapi.openapi.constants as openapi_constants

openapi_utils.validation_error_response_definition = {
    "title": "HTTPValidationError",
    "type": "object",
    "properties": {
        "error": { "title": "Error", "type": "boolean"},
        "message": { "title": "Message", "type": "string"},
        "data": {
            "title": "Data",
            "type": "array",
            "items": {"$ref": openapi_constants.REF_PREFIX + "ValidationError"},
        }
    }
}
