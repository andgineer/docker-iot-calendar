"""Load mathplot images from files."""

from typing import Any

import matplotlib.image as mpimg
import numpy as np
import numpy.typing as npt

from singleton import Singleton


class ImageLoader(metaclass=Singleton):
    """Read matplotlib images from file.

    Cache images that have already been read.
    Return default image if file does not exist or if file name is empty.
    """

    def __init__(self) -> None:
        """Init."""
        self._cache: dict[str, npt.NDArray[Any]] = {}
        self._non_existed: npt.NDArray[Any] = np.array([[[255, 255, 255]]], dtype=np.uint8)

    def by_file_name(self, image_file_name: str) -> npt.NDArray[Any]:
        """Load by file name."""
        if not image_file_name:
            return self._non_existed
        if image_file_name not in self._cache:
            try:
                self._cache[image_file_name] = mpimg.imread(image_file_name)
            except Exception as e:  # noqa: BLE001
                print("#" * 5, f" Error reading image from {image_file_name}:\n{e}")
                return self._non_existed
        return self._cache[image_file_name]
