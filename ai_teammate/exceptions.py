"""AI Teammate SDK Exceptions"""

from typing import Optional, List


class AITeammateError(Exception):
    """Base exception for AI Teammate SDK"""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AuthenticationError(AITeammateError):
    """Invalid or missing API key"""
    pass


class RateLimitError(AITeammateError):
    """Rate limit exceeded"""
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class NotFoundError(AITeammateError):
    """Resource not found"""
    
    def __init__(self, message: str, resource_type: Optional[str] = None):
        super().__init__(message, status_code=404)
        self.resource_type = resource_type


class ValidationError(AITeammateError):
    """Invalid request parameters"""
    
    def __init__(self, message: str, errors: Optional[List] = None):
        super().__init__(message, status_code=400)
        self.errors = errors or []


class ServerError(AITeammateError):
    """Server-side error"""
    pass
