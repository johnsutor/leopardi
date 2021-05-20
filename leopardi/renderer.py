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

    """

    def __init__(
        self,
        labels: Union[str, list] = None,
        resolution_x: int = 1024,
        resolution_y: int = 1024,
        render_engine: str = "BLENDER_EEVEE",
        use_shadow: bool = False,
    ):
        self._label_modes = [
            "YOLO",
            "COCO",
            "PASCAL",
            "DEPTH",
        ]

        self.resolution_x = resolution_x
        self.resolution_y = resolution_y
        self.render_engine = render_engine
        self.use_shadow = use_shadow
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

        assert render_engine in [
            "BLENDER_EEVEE",
            "CYCLES",
        ], f"{render_engine} is not a supported render engine"

        self.labels = labels
        self.render_engine = render_engine

    def __call__(self):
        return f" -l {' '.join(self.labels) if self.labels else ''} -rx {self.resolution_x} -ry {self.resolution_y} -re {self.render_engine} {'-s' if self.use_shadow else ''} "
