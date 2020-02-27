from datetime import datetime

from flask import request
from flask_restx import Namespace, fields, Resource

import app.db_model as db
from app.errors.exceptions import BackendError


class CryptoDto:
    """
    Crypto data transfer object
    """
    exchanges_api = Namespace('exchanges', description='Crypto exchanges operations')
    exchange_post = exchanges_api.model('exchange post', {
        'name': fields.String(required=True, description='Name of the exchange'),
        'currency_shortcut': fields.String(required=True, description='Currency shortcut(3 letter)'),
        'currency_name': fields.String(description='Currency name')
    })
    exchange_deposit = exchanges_api.model('deposit exchange', {
        'amount': fields.Float(required=True, description='Deposit exchange amount')
    })
    currency = exchanges_api.model('currency', {
        'id': fields.Integer(description='ID of the currency'),
        'shortcut': fields.String(description='Currency shortcut(3 letter)'),
        'name': fields.String(description='Currency name'),
        'actual_rate': fields.Float(description='Actual rate for the given exchange currency')
    })
    currencies = exchanges_api.model('currencies updates', {
        'method': fields.String(required=True, enum=['POST', 'PUT', 'DELETE'],
                                description='Method for the crypto-currency'),
        'currency': fields.Nested(currency, required=True, description='Crypto-currency parameters')
    })
    trade = exchanges_api.model('trade', {
        'amount': fields.Float(required=True, description='Amount of the transaction'),
        'currency_in': fields.String(required=True, description='Currency in the trade'),
        'currency_out': fields.String(required=True, description='Currency out the trade'),
    })

    history_api = Namespace('history', description='History of all trades within all exchanges')
    history = history_api.model('trades history', {

    })


exchanges_api = CryptoDto.exchanges_api
_exchange_post = CryptoDto.exchange_post
_exchange_deposit = CryptoDto.exchange_deposit
_currencies = CryptoDto.currencies
_trade = CryptoDto.trade
history_api = CryptoDto.history_api

_history_parser = history_api.parser()
_history_parser.add_argument('offset', type=int, location='args', help='History offset')
_history_parser.add_argument('limit', type=int, location='args', help='History of trades limit')
_history_parser.add_argument('exchange_id', type=int, location='args', help='Trades from exchange')
_history_parser.add_argument('search', type=str, location='args', help='Search query')
_history_parser.add_argument('date_from', type=str, location='args',
                             help='Trades from date format: "%Y-%m-%dT%H:%M:%SZ"')
_history_parser.add_argument('date_to', type=str, location='args',
                             help='Trades to date format: "%Y-%m-%dT%H:%M:%SZ"')


@exchanges_api.route('')
class CryptoExchange(Resource):

    @exchanges_api.expect(_exchange_post, validate=True)
    def post(self):
        """ Add new crypto exchange """
        name = request.json.get('name')
        currency_shortcut = request.json.get('currency_shortcut').upper()
        currency_name = request.json.get('currency_name', None)

        if len(currency_shortcut) != 3 or not currency_shortcut.isalpha():
            raise ValueError(f'Value "currency_shortcut"({currency_shortcut}) is not alphabetic or length is not 3.')
        if not name.isalpha():
            raise ValueError(f'Value "name"({name}) is not alphabetic.')
        if currency_name and not currency_name.isalpha():
            raise ValueError(f'Value "currency_name"({currency_name}) is not alphabetic.')

        if not db.Exchange.query.filter_by(name=name).first():
            currency = db.Currency(name=currency_name, shortcut=currency_shortcut, actual_rate=1, crypto=False)
            exchange = db.Exchange(name=name, currency=[currency])
            db.add_object(currency)
            db.save_changes(exchange)

            return db.exchange_schema.dump(exchange), 201
        else:
            raise BackendError(f'Exchange with name: {name} is already exists.')


@exchanges_api.route("/<int:exchange_id>")
@exchanges_api.param('exchange_id', 'Exchange id')
class ExchangeDeposit(Resource):

    @exchanges_api.expect(_exchange_deposit, validate=True)
    def post(self, exchange_id):
        """ Deposit to the exchange """
        amount = request.json.get('amount')
        exchange = db.Exchange.query.get(exchange_id)

        if not exchange:
            raise BackendError(f'Exchange with id: {exchange_id} does not exist.')

        exchange.currency[0].total += amount  # first currency is the exchange currency
        db.save_changes()

        return {"status": "success"}, 200


@exchanges_api.route("/<int:exchange_id>/currencie")
@exchanges_api.param('exchange_id', 'Exchange id')
class ExchangeCurrencies(Resource):

    @exchanges_api.expect([_currencies], validate=True)
    def put(self, exchange_id):
        """ Update crypto-currencies within exchange """
        data = request.json
        exchange = db.Exchange.query.get(exchange_id)

        if not exchange:
            raise BackendError(f'Exchange with id: {exchange_id} does not exist.')

        for item in data:
            method = item.get('method')

            # --------- Create ---------
            if method == 'POST':
                name = item["currency"].get('name', None)
                shortcut = item["currency"].get('shortcut').upper()
                actual_rate = item["currency"].get('actual_rate')

                if not shortcut:
                    raise BackendError('Missing currency shortcut.')
                elif len(shortcut) != 3 or not shortcut.isalpha():
                    raise ValueError(f'Value "shortcut"({shortcut}) is not alphabetic or length is not 3.')
                if name and not name.isalpha():
                    raise ValueError(f'Value "name"({name}) is not alphabetic.')
                if not actual_rate:
                    raise BackendError('Missing currency actual_rate.')

                currency = db.Currency(name=name, shortcut=shortcut, actual_rate=actual_rate, exchange_id=exchange_id,
                                       crypto=True)
                db.add_object(currency)

            # --------- Edit ---------
            elif method == 'PUT':
                cur_id = item["currency"].get('id')
                name = item["currency"].get('name', None)
                shortcut = item["currency"].get('shortcut', None).upper()
                actual_rate = item["currency"].get('actual_rate', None)

                if not cur_id:
                    raise BackendError('Missing currency id for editing.')

                currency = db.Currency.query.filter_by(id=cur_id, exchange_id=exchange_id, crypto=True).first()
                if not currency:
                    raise BackendError(f'Crypto-currency with id: {cur_id} does not exist.')

                if name:
                    currency.name = name
                if shortcut:
                    currency.shortcut = shortcut
                if actual_rate:
                    currency.actual_rate = actual_rate

            # --------- Delete ---------
            elif method == 'DELETE':
                cur_id = item["currency"].get('id')
                db.Currency.query.filter_by(id=cur_id, exchange_id=exchange_id).delete()

        db.save_changes()
        currencies = db.Currency.query.filter_by(exchange_id=exchange_id).all()

        return db.currencies_schema.dump(currencies), 200


@exchanges_api.route("/<int:exchange_id>/trades")
@exchanges_api.param('exchange_id', 'Exchange id')
class ExchangeTrade(Resource):

    @exchanges_api.expect(_trade, validate=True)
    def post(self, exchange_id):
        """ Create trade """
        amount = request.json.get('amount')
        shortcut_in = request.json.get('currency_in').upper()
        shortcut_out = request.json.get('currency_out').upper()

        if len(shortcut_in) != 3 or not shortcut_in.isalpha():
            raise ValueError(f'Value "currency_in"({shortcut_in}) is not alphabetic or length is not 3.')
        if len(shortcut_out) != 3 or not shortcut_out.isalpha():
            raise ValueError(f'Value "currency_out"({shortcut_out}) is not alphabetic or length is not 3.')

        if shortcut_in == shortcut_out:
            raise BackendError('Currency in and out is the same.')

        exchange = db.Exchange.query.get(exchange_id)

        if not exchange:
            raise BackendError(f'Exchange with id: {exchange_id} does not exist')

        currency_in = db.Currency.query.filter_by(shortcut=shortcut_in, exchange_id=exchange_id).first()
        currency_out = db.Currency.query.filter_by(shortcut=shortcut_out, exchange_id=exchange_id).first()

        if not currency_in:
            raise BackendError(f'Shortcut: {shortcut_in} does not exist for the exchange.')
        if not currency_out:
            raise BackendError(f'Shortcut: {shortcut_out} does not exist for the exchange.')

        if currency_in.total < amount:
            raise BackendError(f'Not enough currency to trade, actual:{currency_in.total} and trade amount: {amount}')

        # currency in must convert to exchange currency and than into currency out
        result_value = amount*currency_in.actual_rate*currency_out.actual_rate

        currency_in.total -= amount
        currency_out.total += result_value

        trade = db.Trade(exchange_id=exchange_id, amount=amount, currency_in=currency_in, currency_out=currency_out)
        db.save_changes(trade)

        return {"status": "success"}, 200


@history_api.route('')
class HistoryAPI(Resource):

    @history_api.expect(_history_parser, validate=True)
    def get(self):
        """ Get all trades within all exchanges """
        args = _history_parser.parse_args()

        query = db.Trade.query
        if args.exchange_id:
            query = query.filter_by(exchange_id=args.exchange_id)
        if args.date_from:
            date = datetime.strptime(args.date_from, '%Y-%m-%dT%H:%M:%SZ')
            query = query.filter(db.Trade.date >= date)
        if args.date_to:
            date = datetime.strptime(args.date_to, '%Y-%m-%dT%H:%M:%SZ')
            query = query.filter(db.Trade.date <= date)
        if args.search:
            currencies = db.Currency.query.filter(db.Currency.name.like('%' + args.search + '%')).all()
            currencies = [currency.id for currency in currencies]
            query = query.filter((db.Trade.currency_in_id.in_(currencies)) | (db.Trade.currency_out_id.in_(currencies)))

        result = query.offset(args.offset).limit(args.limit).all()

        return db.trades_schema.dump(result), 200
