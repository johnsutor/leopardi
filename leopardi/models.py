"""
Author: John Sutor
Date: May 8th, 2020

This folder contains utilities and classes for loading in models from 
a directory containing model files.

"""

import os
import random
from typing import Callable, Optional, Any


class ModelLoader:
    """
    The base model loading class

    Args:

    """

    def __init__(
        self,
        model_directory: str = "./models/",
        model_mode: str = "random",
        sampling_fn: Optional[Callable[[str], Any]] = None,
    ):

        self._model_modes = ["random", "iterative"]
        self._model_formats = (".fbx", ".obj")

        self._model_directory = model_directory
        self.model_mode = model_mode

        assert (
            self.model_mode in self._model_modes
        ), "You must use a built-in model loading method"

        self._sampling_fn = sampling_fn

        assert self.__len__() > 0, "You must have at least one model in the models directory"

    def __len__(self):
        return len(
            [
                f
                for f in os.listdir(self._model_directory)
                if os.path.isfile(self._model_directory + f) and f.endswith(self._model_formats)
            ]
        )

    def __call__(self, n: int = None):
        if self._sampling_fn is not None:
            return self._sampling_fn(self._model_directory)

        elif self.model_mode is "random":
            model = random.choice(
                [
                f
                for f in os.listdir(self._model_directory)
                if os.path.isfile(self._model_directory + f) and f.endswith(self._model_formats)
            ]
            )

        elif self.model_mode is "iterative":
            assert (
                n is not None
            ), "You must provide the iteration to use iterative loading"
            model = [
                f
                for f in os.listdir(self._model_directory)
                if os.path.isfile(self._model_directory + f) and f.endswith(self._model_formats)
            ][n % self.__len__()]

        return os.path.realpath(self._model_directory) + "/" + model