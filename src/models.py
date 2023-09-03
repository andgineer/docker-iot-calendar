from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class WeatherData(BaseModel):
    """Weather data."""

    temp_min: List[Optional[float]]
    temp_max: List[Optional[float]]
    images_folder: Optional[str] = None
    icon: List[str]
    day: List[datetime]
