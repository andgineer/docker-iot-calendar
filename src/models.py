from datetime import datetime
from typing import List

from pydantic import BaseModel


class WeatherData(BaseModel):
    """Weather data."""

    temp_min: List[float]
    temp_max: List[float]
    images_folder: str = None
    icon: List[str]
    day: List[datetime]
