"""
Custom exception handlers for OpenRoute.ai API
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Log the error
        logger.error(
            f"API Error: {exc.__class__.__name__} - {str(exc)}",
            exc_info=True,
            extra={'context': context}
        )

        # Customize the response data
        custom_response_data = {
            'error': {
                'message': str(exc),
                'type': exc.__class__.__name__,
                'status_code': response.status_code,
            }
        }

        # Add field errors if they exist
        if hasattr(response, 'data') and isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_response_data['error']['detail'] = response.data['detail']
            else:
                custom_response_data['error']['fields'] = response.data

        response.data = custom_response_data

    else:
        # Handle unexpected errors
        logger.error(
            f"Unhandled Exception: {exc.__class__.__name__} - {str(exc)}",
            exc_info=True,
            extra={'context': context}
        )

        response = Response(
            {
                'error': {
                    'message': 'An unexpected error occurred. Please try again later.',
                    'type': 'ServerError',
                    'status_code': 500,
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response


class ValidationError(Exception):
    """Custom validation error"""
    pass


class ResourceNotFoundError(Exception):
    """Custom resource not found error"""
    pass


class PermissionDeniedError(Exception):
    """Custom permission denied error"""
    pass
