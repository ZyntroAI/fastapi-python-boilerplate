"""Standardized GraphQL errors — carry code/status extensions."""

from strawberry.exceptions import StrawberryGraphQLError


class PermissionDenied(StrawberryGraphQLError):
    def __init__(self, message="Forbidden", code="PERMISSION_DENIED"):
        super().__init__(message, extensions={"code": code, "status": 403})


class AuthenticationRequired(StrawberryGraphQLError):
    def __init__(self, message="Unauthenticated", code="UNAUTHENTICATED"):
        super().__init__(message, extensions={"code": code, "status": 401})


class ResourceNotFound(StrawberryGraphQLError):
    def __init__(self, message="Not found", code="NOT_FOUND"):
        super().__init__(message, extensions={"code": code, "status": 404})
