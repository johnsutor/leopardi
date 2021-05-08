"""
Author: John Sutor
Date: May 8th, 2020

This folder contains utilities and classes for loading in backgrounds from 
a directory containing background images.

"""

import os
import random
from typing import Callable
from PIL import Image


class BackgroundLoader:
    """
    The base background loading class

    Args:

    """

    def __init__(
        self,
        background_directory: str = "/backgrounds",
        background_mode: str = "random",
        sampling_fn: Callable = None,
    ):

        self._background_modes = ["random", "iterative"]
        self._image_formats = [".jpg", ".png", ".gif"]

        self._background_directory = background_directory
        self.background_mode = background_directory

        assert (
            self.background_mode in self._background_modes
        ), "You must use a built-in background loading method"

        self._sampling_fn = sampling_fn

    def __len__(self):
        return len(
            [
                f
                for f in os.listdir(self._background_directory)
                if os.path.isfile(f) and f[:-4] in self._image_formats
            ]
        )

    def __call__(self, n: int = None):
        if self._sampling_fn is not None:
            return self._sampling_fn(self._background_directory)

        elif self.background_mode is "random":
            img = random.choice(
                [
                    f
                    for f in os.listdir(self._background_directory)
                    if os.path.isfile(f) and f[:-4] in self._image_formats
                ]
            )

        elif self.background_mode is "iterative":
            assert (
                n is not None
            ), "You must provide the iteration to use iterative loading"
            img = [
                f
                for f in os.listdir(self._background_directory)
                if os.path.isfile(f) and f[:-4] in self._image_formats
            ][n % self.__len__()]

        return Image.open(self.background_mode + "/" + img)
