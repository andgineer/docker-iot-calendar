"""Read matplotlib images from file, cache images that already read."""


import matplotlib.image as mpimg
import numpy as np


class CachedImage(object):
    _cache = {}
    _empty = np.array([[[255, 255, 255]]], dtype=np.uint8)
    def by_file_name(self, image_file_name):
        """
        :param image_file_name:
        :return:
            image from file (or from cache)
            empty image if image_file_name empty or file does not exists
        """

        if not image_file_name:
            return self._empty
        if image_file_name not in self._cache:
            try:
                self._cache[image_file_name] = mpimg.imread(image_file_name)
            except Exception as e:
                print('#'*5, ' Error reading image from {}:\n{}'.format(image_file_name, e))
                return self._empty
        return self._cache[image_file_name]