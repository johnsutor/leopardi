"""
Author: John Sutor
Date: May 7th, 2020

This file contains the code for the Leopardi class, from which
the functionality of the Leopardi codebase is derived

"""

import os
import platform


class Leopardi:
    """
    The base class for the Leopardi library

    Args:

    """

    def __init__(
        self,
        background_directory: str = "/backgrounds",
        model_directory: str = "/models",
        blender_directory: str = None,
    ):

        self._work_directory = os.getcwd()
        self._model_directory = model_directory
        self._background_directory = background_directory

        # Find the Blender directory based on OS
        SYSTEM = platform.system()

        if blender_directory is None:
            if SYSTEM is "Windows":
                pass
            elif SYSTEM is "Linux":
                pass
            elif SYSTEM is "Darwin":
                pass
            else:
                raise Exception(
                    "Unable to locate the Blender Install. Please provide Blender's location as an argument, or install Blender if you haven't done so already."
                )
        else:
            self._blender_directory = blender_directory

    def render(self, N):
        pass
