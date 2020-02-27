import datetime

from flask import current_app as app
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
ma = Marshmallow()


def todict(obj):
    """
    Return the object's dict excluding private attributes,
    sqlalchemy state and relationship attributes.
    """
    excl = ('_sa_adapter', '_sa_instance_state')
    return {k: v for k, v in vars(obj).items() if not k.startswith('_') and
            not any(hasattr(v, a) for a in excl)}


class Currency(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    shortcut = db.Column(db.String(3), nullable=False)
    actual_rate = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False, default=0)
    exchange_id = db.Column(db.Integer, db.ForeignKey('exchange.id'))
    crypto = db.Column(db.Boolean, nullable=False)

    __table_args__ = (db.UniqueConstraint('shortcut', 'exchange_id', name='unique_shortcut_exchange'),)

    def __repr__(self):
        params = ', '.join(f'{k}={v}' for k, v in todict(self).items())
        return f'<{self.__class__.__name__}({params})>'


class Trade(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    currency_in_id = db.Column(db.Integer, db.ForeignKey('currency.id'), nullable=False)
    currency_out_id = db.Column(db.Integer, db.ForeignKey('currency.id'), nullable=False)
    exchange_id = db.Column(db.Integer, db.ForeignKey('exchange.id'), nullable=False)
    date = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    currency_in = db.relationship('Currency', lazy=False, foreign_keys='Trade.currency_in_id')
    currency_out = db.relationship('Currency', lazy=False, foreign_keys='Trade.currency_out_id')

    def __repr__(self):
        params = ', '.join(f'{k}={v}' for k, v in todict(self).items())
        return f'<{self.__class__.__name__}({params})>'


class Exchange(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    currency = db.relationship('Currency', backref='exchange', lazy=True)
    trades = db.relationship('Trade', backref='exchange', lazy=True)

    def __repr__(self):
        params = ', '.join(f'{k}={v}' for k, v in todict(self).items())
        return f'<{self.__class__.__name__}({params})>'


class CurrencySchema(ma.ModelSchema):
    class Meta:
        model = Currency


class ExchangeSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'currency')

    currency = ma.Nested(CurrencySchema, many=True)


class TradeSchema(ma.ModelSchema):
    class Meta:
        model = Trade

    currency_in = ma.Nested(CurrencySchema)
    currency_out = ma.Nested(CurrencySchema)


def save_changes(instance=None):
    """
    Commit changes into DB

    :param instance: DB object to push
    """
    app.logger.info(f'Commit changes and add object({instance}) into DB')
    if instance:
        db.session.add(instance)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def add_object(instance):
    """
    Add object into DB session
    :param instance: DB object
    """
    app.logger.info(f'Add object: {instance} into DB session')
    db.session.add(instance)


# feature
def get_or_create(model, **kwargs):
    """
    Get or create db object without commit

    :param class model: DB class
    :param kwargs: kwargs
    """
    app.logger.info(f'Get of create object of {model} with arguments: {kwargs}')
    instance = model.query.filter_by(**kwargs).first()

    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        return instance


exchange_schema = ExchangeSchema()
currencies_schema = CurrencySchema(many=True)
trades_schema = TradeSchema(many=True)
