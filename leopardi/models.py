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
    """The base model loading class"""
    model_directory: str = "./models/"
    """The directory containing either .fbx or .obj models to be rendered."""
    model_mode: str = "RANDOM"
    """ The method for choosing a model to be rendered. Must be one of ["RANDOM", "ITERATIVE"]"""
    sampling_fn: Optional[Callable]
    """A function to be used to sample models. Should return a single string representing a path to a model."""

    def __init__(
        self,
        model_directory: str = "./models/",
        model_mode: str = "RANDOM",
        sampling_fn: Optional[Callable[[str], Any]] = None,
    ):
        self._model_modes = ["RANDOM", "ITERATIVE"]
        self._model_formats = (".fbx", ".obj")

        model_mode = model_mode.upper().strip()

        assert (
            model_mode in self._model_modes
        ), "You must use a built-in model loading method"

        self._model_directory = os.path.realpath(model_directory) + "/"
        self.model_mode = model_mode

        self._sampling_fn = sampling_fn

        assert (
            self.__len__() > 0
        ), "You must have at least one model in the models directory"

    def __len__(self):
        return len(
            [
                f
                for f in os.listdir(self._model_directory)
                if os.path.isfile(self._model_directory + f)
                and f.endswith(self._model_formats)
            ]
        )

    def __call__(self, n: int = None):
        if self._sampling_fn is not None:
            return self._sampling_fn(self._model_directory)

        elif self.model_mode == "RANDOM":
            model = random.choice(
                [
                    f
                    for f in os.listdir(self._model_directory)
                    if os.path.isfile(self._model_directory + f)
                    and f.endswith(self._model_formats)
                ]
            )

        elif self.model_mode == "ITERATIVE":
            assert (
                n is not None
            ), "You must provide the iteration to use iterative loading"
            model = [
                f
                for f in os.listdir(self._model_directory)
                if os.path.isfile(self._model_directory + f)
                and f.endswith(self._model_formats)
            ][n % self.__len__()]

        return os.path.realpath(self._model_directory) + "/" + model
