"""
Author: John Sutor
Date: May 8th, 2020

This folder contains utilities and classes for positioning and rendering camera 
information

"""

import os
import random
from math import pi, sqrt, atan, sin, cos


class BlenderCamera:
    """
    The base camera class for rendering within Blender

    Args:

    """

    def __init__(
        self,
        camera_mode: str = "random",
        camera_type: str = "random",
        fov_x: float = 0.0,
        fov_y: float = 0.0,
        lens: float = 50.0,
        sensor_height: float = 24.0,
        sensor_width: float = 36.0,
        phi_min: float = 0.0,
        phi_max: float = pi / 2.0,
        theta_min: float = 0.0,
        theta_max: float = 2.0 * pi,
        radius=1.0,
        **kwargs,
    ):

        self._camera_modes = ["random", "fibonacci", "icosphere"]
        self._camera_types = [".fbx", ".obj"]

        assert camera_mode in self._camera_modes, "You must use a built-in camera mode"

        self.camera_mode = camera_mode
        self.camera_type = camera_type

        assert (
            0.00640536 <= fov_x <= 3.01675
        ), "fov_x must be in range [0.00640536, 3.01675]"
        assert (
            0.00640536 <= fov_y <= 3.01675
        ), "fov_y must be in range [0.00640536, 3.01675]"

        self.fov_x = fov_x
        self.fov_y = fov_y

        assert lens >= 1.0, "lens size must be greater than one millimeter"

        self.lens = lens

        assert sensor_height > 1.0, "Sensor height must be greater than one millimeter"
        assert sensor_width > 1.0, "Sensor width must be greater than one millimeter"

        self.sensor_height = sensor_height
        self.sensor_width = sensor_width

        assert 0.0 <= phi_min < pi / 2.0, "phi_min must be in range [0., pi / 2)"
        assert 0.0 < phi_max <= pi / 2.0, "phi_max must be in range (0., pi / 2]"
        assert phi_min < phi_max, "phi_min must be less than phi_max"

        assert 0.0 <= theta_min < 2.0 * pi, "theta_min must be in range [0., 2 * pi)"
        assert 0.0 < theta_max <= 2.0 * pi, "theta_max must be in range (0., 2 * pi]"
        assert theta_min < theta_max, "theta_min must be less than theta_max"

        self.phi_min = phi_min
        self.phi_max = phi_max
        self.theta_min = theta_min
        self.theta_max = theta_max

        assert radius > 0.0, "Radius must be greater than zero"
        self.radius = radius

        # Determine predefined points
        #
        # TODO: Generate KWARGS documentation
        #
        if "fibonacci" in self.camera_mode:
            self._predefined_points = self._generate_fibonacci(kwargs["num_points"])

        #
        # TODO: Generate KWARGS documentation
        #
        elif "icosphere" in self.camera_mode:
            self._predefined_points = self._generate_icosphere(kwargs["subdivisions"])

    def __call__(self, n: int = None):
        if self.camera_mode is "random":
            phi = (self.phi_max - self.phi_min) * random.random() + self.phi_min
            theta = (self.theta_max - self.theta_min) * random.random() + self.theta_min

        elif "random" in self.camera_mode:
            return random.choice(self._predefined_points)

        elif "iterate" in self.camera_mode:
            return self._predefined_points[n]

        return self.radius, theta, phi

    def _cartesian_to_spherical(self, x, y, z):
        radius = sqrt(x ** 2 + y ** 2 + z ** 2)
        theta = atan(y / x)
        phi = atan(sqrt(x ** 2 + y ** 2) / z)

        return radius, theta, phi

    def _generate_fibonacci(self, n: int = 1):
        GOLDEN_ANGLE = (3 - sqrt(5)) * pi

        angles = [GOLDEN_ANGLE * i for i in range(n)]

        z = [i / n for i in range(1 - n, n, 2)]

        radii = [sqrt(1 - p ** 2) for p in z]

        x = [r * cos(a) for r, a in zip(radii, angles)]
        y = [r * sin(a) for r, a in zip(radii, angles)]

        verts = list(zip(x, y, z))
        verts = map(self._cartesian_to_spherical, verts)

        return list(verts)

    def _generate_icosphere(self, subdivisions: int = 0):
        """ Copied from: https://sinestesia.co/blog/tutorials/python-icospheres/ """
        if subdivisions > 4:
            import warnings

            warnings.warn(
                "Using a number of subdivisions greater than four may crash the program"
            )

        middle_point_cache = {}

        PHI = (1 + sqrt(5)) / 2

        verts = [
            vertex(-1, PHI, 0),
            vertex(1, PHI, 0),
            vertex(-1, -PHI, 0),
            vertex(1, -PHI, 0),
            vertex(0, -1, PHI),
            vertex(0, 1, PHI),
            vertex(0, -1, -PHI),
            vertex(0, 1, -PHI),
            vertex(PHI, 0, -1),
            vertex(PHI, 0, 1),
            vertex(-PHI, 0, -1),
            vertex(-PHI, 0, 1),
        ]

        faces = [
            [0, 11, 5],
            [0, 5, 1],
            [0, 1, 7],
            [0, 7, 10],
            [0, 10, 11],
            [1, 5, 9],
            [5, 11, 4],
            [11, 10, 2],
            [10, 7, 6],
            [7, 1, 8],
            [3, 9, 4],
            [3, 4, 2],
            [3, 2, 6],
            [3, 6, 8],
            [3, 8, 9],
            [4, 9, 5],
            [2, 4, 11],
            [6, 2, 10],
            [8, 6, 7],
            [9, 8, 1],
        ]

        def vertex(x, y, z):
            length = sqrt(x ** 2 + y ** 2 + z ** 2)

            return [i / length for i in (x, y, z)]

        def middle_point(point_1, point_2):
            smaller_index = min(point_1, point_2)
            greater_index = max(point_1, point_2)

            key = "{0}-{1}".format(smaller_index, greater_index)

            if key in middle_point_cache:
                return middle_point_cache[key]

            vert_1 = verts[point_1]
            vert_2 = verts[point_2]
            middle = [sum(i) / 2 for i in zip(vert_1, vert_2)]

            verts.append(vertex(*middle))

            index = len(verts) - 1
            middle_point_cache[key] = index

            return index

        for _ in range(subdivisions):
            faces_subdiv = []
            for tri in faces:
                v1 = middle_point(tri[0], tri[1])
                v2 = middle_point(tri[1], tri[2])
                v3 = middle_point(tri[2], tri[0])

                faces_subdiv.append([tri[0], v1, v3])
                faces_subdiv.append([tri[1], v2, v1])
                faces_subdiv.append([tri[2], v3, v2])
                faces_subdiv.append([v1, v2, v3])

            faces = faces_subdiv

        verts = map(self._cartesian_to_spherical, verts)

        return list(verts)
