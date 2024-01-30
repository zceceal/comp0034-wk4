# Adapted from https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/quickstart/#define-models
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from complexdb import db


class Temperature(db.Model):
    __tablename__ = "temperature"
    temp_id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    temp_mean: Mapped[float] = mapped_column(db.Float, nullable=False)
    temp_upper: Mapped[float] = mapped_column(db.Float, nullable=False)
    temp_lower: Mapped[float] = mapped_column(db.Float, nullable=False)
    # one-to-many relationship with Prediction, allows you to find predictions associtaed with temperature,
    # https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-many
    predictions: Mapped[List["Prediction"]] = relationship(back_populates="temp")


class Bloom(db.Model):
    __tablename__ = "bloom"
    bloom_id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    day_of_year: Mapped[int] = mapped_column(db.Integer, nullable=False)
    # one-to-many relationship with Prediction
    predictions: Mapped[List["Prediction"]] = relationship(back_populates="bloom_doy")


class Prediction(db.Model):
    __tablename__ = 'prediction'
    year: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    bloom_id: Mapped[int] = mapped_column(ForeignKey("bloom.bloom_id"), nullable=False)
    temp_id: Mapped[int] = mapped_column(ForeignKey("temperature.temp_id"), nullable=False)
    # Relationships to Bloom and Temperature
    bloom_doy: Mapped["Bloom"] = relationship(back_populates="predictions")
    temp: Mapped["Temperature"] = relationship(back_populates="predictions")
