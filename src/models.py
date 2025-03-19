from datetime import datetime

from pydantic import BaseModel, Field


class WeatherData(BaseModel):
    """Weather data."""

    temp_min: list[float]
    temp_max: list[float]
    images_folder: str
    icon: list[str]
    day: list[datetime]


class WeatherLabel(BaseModel):
    """Weather label."""

    summary: str = Field(..., description="The summary of the weather")
    image: str = Field(..., description="The full path to the image to display on the plot")
