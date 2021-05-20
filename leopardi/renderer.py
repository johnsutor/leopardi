"""
Author: John Sutor
Date: May 8th, 2020

This folder contains utilities and classes for loading in models from 
a directory containing model files.

"""

from typing import Union


class LeopardiRenderer:
    """
    The base class for defining rendering specs

    Args:
        labels: (str | list, ["YOLO", "COCO", "PASCAL", "DEPTH"], None) A list of labels or sinle label to generate with each render.
        resolution_x: (int, 1024) The horizontal resolution, in pixels, for the rendered image.
        resolution_y: (int, 1024) The vertical resolution, in pixels, for the rendered image.
        render_engine: (str ["BLENDER_EEVEE", "CYCLES"], "BLENDER_EEVEE") The Blender rendering image used to create renders.
        use_shadow: (bool, False) Whether or not to generate a shadown under an object.
        autoscale: (bool, False) Whether or not to automatically scale an object.
    """

    def __init__(
        self,
        labels: Union[str, list] = None,
        resolution_x: int = 1024,
        resolution_y: int = 1024,
        render_engine: str = "BLENDER_EEVEE",
        use_shadow: bool = False,
        autoscale: bool = False,
    ):
        """
        The base class for defining rendering specs

        Args:
            labels: (str | list, ["YOLO", "COCO", "PASCAL", "DEPTH"], None) A list of labels or sinle label to generate with each render.
            resolution_x: (int, 1024) The horizontal resolution, in pixels, for the rendered image.
            resolution_y: (int, 1024) The vertical resolution, in pixels, for the rendered image.
            render_engine: (str ["BLENDER_EEVEE", "CYCLES"], "BLENDER_EEVEE") The Blender rendering image used to create renders.
            use_shadow: (bool, False) Whether or not to generate a shadown under an object.
            autoscale: (bool, False) Whether or not to auto scale an object.
        """
        self._label_modes = ["YOLO", "COCO", "PASCAL", "DEPTH"]

        self._render_engines = [
            "BLENDER_EEVEE",
            "CYCLES",
        ]

        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.render_engine = render_engine
        self.use_shadow = use_shadow
        self.autoscale = autoscale
        if type(labels) == str:
            labels = labels.upper().strip()
            assert (
                labels in self._label_modes
            ), f"{labels} is not a supported file format"
            labels = [labels]
        elif type(labels) == list:
            labels = list(map(lambda x: x.upper().strip(), labels))
            for label in labels:
                assert (
                    label in self._label_modes
                ), f"{label} is not a supported file format"

        render_engine = render_engine.upper().strip()

        assert (
            render_engine in self._render_engines
        ), f"{render_engine} is not a supported render engine"

        self.labels = labels
        self.render_engine = render_engine

    def __call__(self):
        return f" -l {' '.join(self.labels) if self.labels else ''} -rx {self.resolution_x} -ry {self.resolution_y} -re {self.render_engine} {'-s' if self.use_shadow else ''} {'-as' if self.autoscale else ''}"
