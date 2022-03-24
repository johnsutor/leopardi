"""
Author: John Sutor
Date: May 8th, 2020

This folder contains utilities and classes for loading in backgrounds from 
a directory containing background images.

"""

import os
import random
from typing import Any, Callable, Optional
from PIL import Image


class BackgroundLoader:
    """The base background loading class. This class stores the directory where backgrounds are located, and determines where to load them from."""
    background_directory: str = os.path.join(os.getcwd(), "/backgrounds/")
    """The directory containing all background images to be used in the renderer."""
    background_mode: str = "RANDOM"
    """The method by which to select a background image to be used. Must be one of ["RANDOM", "ITERATIVE"]."""
    sampling_fn: Optional[Callable[[str], Any]] = None
    """A function to be used to sample backgroungs. Should return a single string representing a path to a background image."""

    def __init__(
        self,
        background_directory: str = os.path.join(os.getcwd(), "/backgrounds/"),
        background_mode: str = "RANDOM",
        sampling_fn: Optional[Callable[[str], Any]] = None,
    ):
        self._background_modes = ["RANDOM", "ITERATIVE"]
        self._image_formats = tuple(Image.registered_extensions().keys())

        background_mode = background_mode.upper().strip()

        assert (
            background_mode in self._background_modes
        ), "You must use a built-in background loading method"

        self._background_directory = os.path.realpath(background_directory) + "/"
        self.background_mode = background_mode

        self._sampling_fn = sampling_fn

        assert (
            self.__len__() > 0
        ), "You must have at least one background image in the backgrounds directory"

    def __len__(self):
        return len(
            [
                f
                for f in os.listdir(self._background_directory)
                if os.path.isfile(self._background_directory + f)
                and f.endswith(self._image_formats)
            ]
        )

    def __call__(self, n: int = None):
        if self._sampling_fn is not None:
            return self._sampling_fn(self._background_directory)

        elif self.background_mode == "RANDOM":
            img = random.choice(
                [
                    f
                    for f in os.listdir(self._background_directory)
                    if os.path.isfile(self._background_directory + f)
                    and f.endswith(self._image_formats)
                ]
            )

        elif self.background_mode == "ITERATIVE":
            assert (
                n is not None
            ), "You must provide the iteration to use iterative loading"
            img = [
                f
                for f in os.listdir(self._background_directory)
                if os.path.isfile(f) and f[:-4] in self._image_formats
            ][n % self.__len__()]

        return Image.open(self._background_directory + img).convert("RGBA")
