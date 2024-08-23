from aiohttp import web


class CustomHTTPException(web.HTTPException):
    def __init__(self, status_code, message):
        super().__init__(reason=message)
        self.status_code = status_code


class NotFound(CustomHTTPException):
    def __init__(self, message="Not found"):
        super().__init__(404, message)


class BadRequest(CustomHTTPException):
    def __init__(self, message="Bad request"):
        super().__init__(400, message)


class Unauthorized(CustomHTTPException):
    def __init__(self, message="Unauthorized"):
        super().__init__(401, message)