"""
Author: John Sutor
Date: May 19th, 2020

This file contains utilities and classes for controlling different aspects of leopardi's lighting

"""

from typing import Optional, Union
import random


class LeopardiLighting:
    """The base lighting class for rendering within Blender"""
    types: Union[str, list] = "SUN"
    """The type or types to generate the lighting for the scene. Must be one of or multiple of ["SPOT", "SUN", "POINT", "AREA", "FLASHLIGHT"]"""

    def __init__(self, types: Union[str, list] = "SUN", **kwargs):
        self._lighting_types = ["SPOT", "SUN", "POINT", "AREA", "FLASHLIGHT"]
        self._lighting_modes = ["FIXED", "NORMAL", "UNIFORM"]

        if type(types) == str:
            types = types.upper().strip()
            assert (
                types in self._lighting_types
            ), f"{types} is not a supported lighting type"
            types = [types]
        elif type(types) == list:
            types = list(map(lambda x: x.upper().strip(), types))
            for label in types:
                assert (
                    label in self._lighting_types
                ), f"{label} is not a supported lighting type"

        self.types = types

        for (k, v) in kwargs.items():
            if k.endswith("_mode"):
                v = check_mode(v, self._lighting_modes)
                setattr(self, k, v)

        #
        # TODO: Implement additional lighting settings
        #

    def __call__(self):
        lighting_type = random.choice(self.types)
        return f" -lt {lighting_type}"


def check_mode(mode: str, accepted_types: list):
    """
    Check that a supplied mode type is accepted after sanitization
    """
    mode = mode.upper().strip()
    assert mode in accepted_types, f"{mode} is not a supported settings mode"
    return mode
