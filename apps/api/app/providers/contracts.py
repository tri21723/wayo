from datetime import date
from typing import Annotated, Literal

from pydantic import AwareDatetime, Field, model_validator

from app.schemas import Contract

Measure = Annotated[float, Field(ge=0, allow_inf_nan=False, strict=True)]


class Coordinate(Contract):
    latitude: float = Field(ge=-90, le=90, allow_inf_nan=False)
    longitude: float = Field(ge=-180, le=180, allow_inf_nan=False)


class MatrixRequest(Contract):
    points: list[Coordinate] = Field(min_length=2, max_length=25)
    mode: Literal["driving"] = "driving"


class TravelMatrix(Contract):
    provider: Literal["osrm"] = "osrm"
    mode: Literal["driving"] = "driving"
    retrieved_at: AwareDatetime
    durations_seconds: list[list[Measure | None]]
    distances_meters: list[list[Measure | None]]


class ForecastRequest(Coordinate):
    starts_on: date
    ends_on: date

    @model_validator(mode="after")
    def chronological(self):
        if self.ends_on < self.starts_on or (self.ends_on - self.starts_on).days >= 16:
            raise ValueError("Forecast range must contain 1–16 days.")
        return self


class WeatherHour(Contract):
    at: AwareDatetime
    precipitation_mm: Measure | None
    rain_probability: float | None = Field(ge=0, le=100, allow_inf_nan=False, strict=True)


class WeatherForecast(Contract):
    provider: Literal["open-meteo"] = "open-meteo"
    retrieved_at: AwareDatetime
    hours: list[WeatherHour]
    attribution: Literal["Weather data by Open-Meteo (CC BY 4.0)"] = (
        "Weather data by Open-Meteo (CC BY 4.0)"
    )
