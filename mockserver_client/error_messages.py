from typing import Dict

common_error_messages: Dict[int, str] = {
    400: "Bad request",
    401: "Authentication credentials were not provided",
    403: "You do not have permission to access this resource",
    404: "The requested resource could not be found",
    500: "An unexpected error occurred on the server",
}
