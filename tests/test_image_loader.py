import pytest
from unittest.mock import patch, Mock
from image_loader import ImageLoader
import numpy as np


class TestImageLoader:
    @pytest.fixture
    def loader(self):
        return ImageLoader()

    def test_load_existing_image(self, loader):
        fake_image = np.array([[[0, 0, 0]]], dtype=np.uint8)

        # Mocking the imread method to return our fake image
        with patch('image_loader.mpimg.imread', return_value=fake_image):
            result = loader.by_file_name('exists.png')

        assert np.array_equal(result, fake_image)

    def test_cache_image(self, loader):
        fake_image = np.array([[[0, 0, 0]]], dtype=np.uint8)

        with patch('image_loader.mpimg.imread', return_value=fake_image) as mock_imread:
            loader.by_file_name('exists.png')
            loader.by_file_name('exists.png')

        # Ensure the image was read only once, hence cached
        mock_imread.assert_called_once()

    def test_load_non_existing_image(self, loader):
        with patch('image_loader.mpimg.imread', side_effect=Exception('File not found')):
            result = loader.by_file_name('non_exists.png')

        assert np.array_equal(result, loader._non_existed)

    def test_empty_file_name(self, loader):
        result = loader.by_file_name('')
        assert np.array_equal(result, loader._non_existed)

    def test_print_error_on_exception(self, loader, capsys):
        with patch('image_loader.mpimg.imread', side_effect=Exception('Some error')):
            loader.by_file_name('error.png')

        captured = capsys.readouterr()
        assert 'Error reading image from error.png' in captured.out

