from complexdb.models import Prediction, Bloom, Temperature
from complexdb import db, ma


class BloomSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Bloom
        include_fk = True
        load_instance = True
        sqla_session = db.session
        include_relationships = True
    # This is the only field needed
    day_of_year = ma.auto_field()


class TemperatureSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Temperature
        include_fk = True
        load_instance = True
        sqla_session = db.session
        include_relationships = True

    # This is the only field needed
    temp_mean = ma.auto_field()
    temp_upper = ma.auto_field()
    temp_lower = ma.auto_field()


class PredictionSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Prediction
        load_instance = True
        sqla_session = db.session
        include_relationships = True

    # Year field from Prediction class and the nested schemas for the Bloom and Temperature
    year = ma.auto_field()
    bloom_doy = ma.Nested(BloomSchema)
    temp = ma.Nested(TemperatureSchema)
