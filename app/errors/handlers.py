from flask import current_app as app
from werkzeug.exceptions import NotFound

from .exceptions import BackendError
from app.api1 import api1


@api1.errorhandler(BackendError)
def backend_exception(error):
    """ Return error message and 400 status code"""
    app.logger.exception(error)
    return {"message": error.message}, 400


@api1.errorhandler(NotFound)
def handle_no_result_exception(_):
    """Return a custom not found error message and 404 status code"""
    return {'message': 'Page not found'}, 404


@api1.errorhandler(Exception)
def unhandled_exception(error):
    """ Return  unhandled exception message and 400 status code"""
    app.logger.exception('Unhandled Exception: %s', error)
    return {"message": str(error)}, 400


@api1.errorhandler
def internal_server_error(error):
    """ Internal server error"""
    app.logger.exception('Server Error: %s', error)
    return {"message": error}, 500
