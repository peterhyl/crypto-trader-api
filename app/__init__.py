import logging
import logging.config
import os

from flask import Flask

from config import config_by_env, LOG_DIR


def create_app():
    app = Flask(__name__)

    app.config.from_object(config_by_env)

    from app.db_model import db, ma
    from app.api1 import bp1
    app.register_blueprint(bp1)

    from app.errors import handlers

    os.makedirs(LOG_DIR, exist_ok=True)
    logging.config.dictConfig(app.config['LOG_CONFIG'])
    app.logger = logging.getLogger('backend.app')

    db.init_app(app)
    ma.init_app(app)

    with app.app_context():
        db.create_all()

    app.logger.info('Crypto trader service startup')

    return app
