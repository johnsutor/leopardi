"""
Author: John Sutor
Date: May 7th, 2020

This file contains the code for the Leopardi class, from which
the functionality of the Leopardi codebase is derived

"""

from .backgrounds import BackgroundLoader
from .camera import LeopardiCamera
from .models import ModelLoader
from .renderer import LeopardiRenderer
from .lighting import LeopardiLighting
import os
import platform
import importlib
import signal
from joblib import Parallel, delayed
from PIL import Image


class Leopardi:
    """
    The base class for the Leopardi library

    Args:
        camera: (leopardi.LeopardiCamera) A LeopardiCamera class, either with the default arguments or additional arguments.
        lighting: (leopardi.LeopardiLighting) A LeopardiLighting class, either with the default arguments or additional arguments.
        renderer: (leopardi.LeopardiRenderer) A LeopardiRenderer class, either with the default arguments or additional arguments.
        background_loader: (leopardi.BackgroundLoader) A BackgroundLoader class, either with the default arguments or additional arguments.
        model_loader: (leopardi.ModelLoader) A ModelLoader class, either with the default arguments or additional arguments.
        blender_directory (str, None) The path to the directory containing the blender.exe file. If no path is provided, Leopardi will attempt to search for this file based on the operating system.
        render_directory (str, "./renders") The path to the directory to hold all renders.
        num_jobs (int, 1) The number of jobs to dispatch when rendering and applying backgrounds, according to the JobLib package. To use all available cores on the CPU, use -1.
    """

    def __init__(
        self,
        camera: LeopardiCamera,
        lighting: LeopardiLighting,
        renderer: LeopardiRenderer,
        background_loader: BackgroundLoader,
        model_loader: ModelLoader,
        blender_directory: str = None,
        render_directory: str = "./renders",
        num_jobs: int = 1,
    ):
        """
        The base class for the Leopardi library

        Args:
            camera: (leopardi.LeopardiCamera) A LeopardiCamera class, either with the default arguments or additional arguments.
            lighting: (leopardi.LeopardiLighting) A LeopardiLighting class, either with the default arguments or additional arguments.
            renderer: (leopardi.LeopardiRenderer) A LeopardiRenderer class, either with the default arguments or additional arguments.
            background_loader: (leopardi.BackgroundLoader) A BackgroundLoader class, either with the default arguments or additional arguments.
            model_loader: (leopardi.ModelLoader) A ModelLoader class, either with the default arguments or additional arguments.
            blender_directory (str, None) The path to the directory containing the blender.exe file. If no path is provided, Leopardi will attempt to search for this file based on the operating system.
            render_directory (str, "./renders") The path to the directory to hold all renders.
            num_jobs (int, 1) The number of jobs to dispatch when rendering and applying backgrounds, according to the JobLib package. To use all available cores on the CPU, use -1.
        """

        SYSTEM = platform.system()
        if blender_directory is None:
            if SYSTEM == "Windows":
                if os.path.isdir("C:/Program Files/Blender Foundation/"):
                    # Fetch most up-to-date
                    try:
                        dir = os.listdir("C:/Program Files/Blender Foundation/")
                        dir.sort()
                        dir = "C:/Program Files/Blender Foundation/" + dir[-1] + "/"
                        self._blender_directory = (
                            dir if "blender.exe" in os.listdir(dir) else None
                        )
                    except:
                        pass

                elif os.path.isdir(
                    os.path.expanduser("~") + "/AppData/Roaming/Blender Foundation/"
                ):
                    # Fetch most up-to-date
                    try:
                        dir = os.listdir(
                            os.path.expanduser("~")
                            + "/AppData/Roaming/Blender Foundation/"
                        )
                        dir.sort()
                        dir = (
                            os.path.expanduser("~")
                            + "/AppData/Roaming/Blender Foundation/"
                            + dir[-1]
                            + "/"
                        )
                        self._blender_directory = (
                            dir if "blender.exe" in os.listdir(dir) else None
                        )
                    except:
                        pass
                else:
                    raise Exception(
                        "Unable to locate the Blender Install. Please provide Blender's location as an argument, or install Blender if you haven't done so already."
                    )

            elif SYSTEM == "Linux":
                # /home/mlpc/blender
                if os.path.isdir(os.path.expanduser("~") + "/blender/"):
                    # Fetch most up-to-date
                    try:
                        dir = os.listdir(os.path.expanduser("~") + "/blender/")
                        dir.sort()
                        dir = os.path.expanduser("~") + "/blender/" + dir[-1] + "/"
                        self._blender_directory = (
                            dir if "blender.exe" in os.listdir(dir) else None
                        )
                    except:
                        pass

                else:
                    raise Exception(
                        "Unable to locate the Blender Install. Please provide Blender's location as an argument, or install Blender if you haven't done so already."
                    )
            elif SYSTEM == "Darwin":
                pass
            else:
                raise Exception(
                    "Unable to locate the Blender Install. Please provide Blender's location as an argument, or install Blender if you haven't done so already."
                )
        else:
            self._blender_directory = blender_directory

        self._num_jobs = num_jobs

        self.camera = camera
        self.background_loader = background_loader
        self.model_loader = model_loader
        self.renderer = renderer
        self.lighting = lighting

        self._work_directory = os.getcwd()
        self._model_directory = os.path.realpath(self.model_loader._model_directory)
        self._background_directory = os.path.realpath(
            self.background_loader._background_directory
        )

        if not os.path.isdir(render_directory):
            os.mkdir(render_directory)

        self._render_directory = os.path.realpath(render_directory)
        self._script_directory = importlib.util.find_spec(
            "leopardi"
        ).submodule_search_locations[0]

        # Create render config files as needed
        if self.renderer.labels:
            if "YOLO" in self.renderer.labels:
                with open(self._render_directory + "/classes.txt", "w") as f:
                    f.truncate(0)
                for m in os.listdir(self.model_loader._model_directory):
                    with open(self._render_directory + "/classes.txt", "a") as f:
                        f.write(str(m[:-4]) + "\n")

    def render(self, n: int = 0):
        try:
            os.chdir(self._blender_directory)
            Parallel(n_jobs=self._num_jobs, temp_folder="/tmp")(
                delayed(self._render_single)(i) for i in range(n)
            )

            os.chdir(self._work_directory)
            Parallel(n_jobs=self._num_jobs, temp_folder="/tmp")(
                delayed(self._apply_background)(i) for i in range(n)
            )

        except:
            os.chdir(self._work_directory)

    def _render_single(self, i: int):
        camera_settings = self.camera()
        model = self.model_loader(i)
        render = self.renderer()
        lighting_settings = self.lighting()

        os.system(
            "blender -b --python "
            + self._script_directory
            + "/_blender.py -- -wd "
            + self._work_directory
            + " -rc "
            + str(i)
            + camera_settings
            + lighting_settings
            + " -m "
            + model
            + " -rd "
            + self._render_directory
            + render
        )

    def _apply_background(self, i):
        background = self.background_loader(i)

        renders = [
            f
            for f in os.listdir(self._render_directory)
            if "render_" in f
            if f.endswith(tuple(Image.registered_extensions().keys()))
        ]

        render = Image.open(self._render_directory + "/" + renders[i]).convert("RGBA")
        rw, rh = render.size

        background = background.resize((rw, rh))

        background.paste(render, (0, 0), mask=render)
        background.save(self._render_directory + "/" + renders[i])
