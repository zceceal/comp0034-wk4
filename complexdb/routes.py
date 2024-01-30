from flask import current_app as app

from complexdb import db
from complexdb.models import Prediction, Bloom, Temperature
from complexdb.schemas import PredictionSchema

# Flask-Marshmallow Schema
predictions_schema = PredictionSchema(many=True)


@app.get("/predictions")
def get_predictions():
    predictions = db.session.execute(
        db.select(Prediction)
    ).scalars()

    # Dump the data using the Marshmallow predictions schema; '.dump()' returns JSON.
    result = predictions_schema.dump(predictions)
    return result