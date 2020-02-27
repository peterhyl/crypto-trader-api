from flask import Blueprint
from flask_restx import Api

from app.api1.crypto import exchanges_api as exchange, history_api as history

bp1 = Blueprint('api1', __name__, url_prefix='/api/v1/crypto')
api1 = Api(bp1,
           title='Crypto trader Api',
           version='1.0',
           description='API functions for trading crypto currency')

api1.add_namespace(exchange)
api1.add_namespace(history)
