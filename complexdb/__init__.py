import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_marshmallow import Marshmallow


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
ma = Marshmallow()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='l-tirPCf1S44mWAGoWqWlA',
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, 'complex.db'),
        SQLALCHEMY_ECHO=True,
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    ma.init_app(app)

    with app.app_context():
        # Create the database and tables if they don't already exist
        from complexdb.models import Prediction, Bloom, Temperature
        db.create_all()

        # Add the data to the database if not already added
        # Pass the sqlalchemy db to the function
        from complexdb.db_utils import add_data
        add_data(db)

        # Register the routes with the app in the context
        from complexdb import routes

    return app
