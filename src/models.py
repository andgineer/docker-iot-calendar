from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class WeatherData(BaseModel):  # type: ignore
    """Weather data."""

    temp_min: List[float]
    temp_max: List[float]
    images_folder: str
    icon: List[str]
    day: List[datetime]


class WeatherLabel(BaseModel):  # type: ignore
    """Weather label."""

    summary: str = Field(..., description="The summary of the weather")
    image: str = Field(..., description="The full path to the image to display on the plot")
