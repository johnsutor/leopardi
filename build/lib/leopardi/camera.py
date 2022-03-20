"""
Author: John Sutor
Date: May 8th, 2020

This folder contains utilities and classes for positioning and rendering camera 
information

"""

import random
from math import pi, sqrt, atan, sin, cos


class LeopardiCamera:
    """
    The base camera class for rendering within Blender

    Args:
        angle_mode: (str ["RANDOM", "FIBONACCI", "ICOSPHERE"], "RANDOM") Method by which to select an angle to position the camera. If either "FIBONACCI" or "ICOSPHERE", this class will render predefined points to choose placement for the camera.
        radius_mode: (str ["FIXED", "UNIFORM", "LOG NORMAL"], "FIXED") Method by which to select a radius to position the camera. "UNIFORM" and "LOG NORMAL" specify random ways of generating a radius, and allow for additional keyword arguments to be passed to set the minimum and maximum radius, as well as the mean and standard deviation of the radius (respectively).
        positional_perturbation: (str ["FIXED", "NORMAL", "UNIFORM"], "FIXED") Method by which to perturb the camera's position in the x, y, and z direction.
        fov_x: (float, 0.00640536) The field of view of the camera horizontally, must be in the range [0.00640536, 3.01675].
        fov_y: (float, 0.00640536) The field of view of the camera vertically, must be in the range [0.00640536, 3.01675].
        lens: (float, 50.0) The size of the camera lens in millimeters. Must be greater than or equal to one millimeter.
        sensor_height: (float, 24.0) The vertical size of the camera sensor in millimeters. Must be greater than or equal to one millimeter.
        sensor_width: (float, 36.0) The horizontal size of the camera sensor in millimeters. Must be greater than or equal to one millimeter.
        phi_min: (float, 0.0) The minimum angle Phi to use for the camera in radians. Must be in the range [0., pi / 2)
        phi_max: (float, pi / 2) The maximum angle Phi to use for the camera in radians. Must be in the range (0., pi / 2]
        theta_min: (float, 0.0) The minimum angle Theta to use for the camera in radians. Must be in the range [0., 2 * pi)
        theta_max: (float, 2 * pi) The maximum angle Theta to use for the camera in radians. Must be in the range (0., 2 * pi]
        radius: (float, 1.0) The radius to be used for fixed rendering
    Keyword Args:
        radius_mean: (float, 0.0) The mean of the log normal distribution to accompany the radius mode "LOG NORMAL"
        radius_std: (float, 1.0) The standard deviation of the log normal distribution to accompany the radius mode "LOG NORMAL"
        radius_min: (float, 0.5) The minimum radius of the uniform distribution to accompany the radius mode "UNIFORM" or "LOG_NORMAL"
        radius_max: (float, 1.5) The maximum radius of the uniform distribution to accompany the radius mode "UNIFORM"
        perturbation_scale: (float, 0.5) The scale applied to the calculated positional perturbations.
    """

    def __init__(
        self,
        angle_mode: str = "RANDOM",
        radius_mode: str = "FIXED",
        positional_perturbation: str = "FIXED",
        fov_x: float = 0.00640536,
        fov_y: float = 0.00640536,
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
        """
        The base camera class for rendering within Blender

        Args:
            angle_mode: (str ["RANDOM", "FIBONACCI", "ICOSPHERE"], "RANDOM") Method by which to select an angle to position the camera. If either "FIBONACCI" or "ICOSPHERE", this class will render predefined points to choose placement for the camera.
            radius_mode: (str ["FIXED", "UNIFORM", "LOG NORMAL"], "FIXED") Method by which to select a radius to position the camera. "UNIFORM" and "LOG NORMAL" specify random ways of generating a radius, and allow for additional keyword arguments to be passed to set the minimum and maximum radius, as well as the mean and standard deviation of the radius (respectively).
            positional_perturbation: (str ["FIXED", "NORMAL", "UNIFORM"], "FIXED") Method by which to perturb the camera's position in the x, y, and z direction.
            fov_x: (float, 0.00640536) The field of view of the camera horizontally, must be in the range [0.00640536, 3.01675].
            fov_y: (float, 0.00640536) The field of view of the camera vertically, must be in the range [0.00640536, 3.01675].
            lens: (float, 50.0) The size of the camera lens in millimeters. Must be greater than or equal to one millimeter.
            sensor_height: (float, 24.0) The vertical size of the camera sensor in millimeters. Must be greater than or equal to one millimeter.
            sensor_width: (float, 36.0) The horizontal size of the camera sensor in millimeters. Must be greater than or equal to one millimeter.
            phi_min: (float, 0.0) The minimum angle Phi to use for the camera in radians. Must be in the range [0., pi / 2)
            phi_max: (float, pi / 2) The maximum angle Phi to use for the camera in radians. Must be in the range (0., pi / 2]
            theta_min: (float, 0.0) The minimum angle Theta to use for the camera in radians. Must be in the range [0., 2 * pi)
            theta_max: (float, 2 * pi) The maximum angle Theta to use for the camera in radians. Must be in the range (0., 2 * pi]
            radius: (float, 1.0) The radius to be used for fixed rendering
        Keyword Args:
            angle_selection: (["RANDOM", "ITERATE"], "RANDOM") The method by which to select the angle from either the Fibonacci or Icosphere angle methods
            radius_mean: (float, 0.0) The mean of the log normal distribution to accompany the radius mode "LOG NORMAL"
            radius_std: (float, 1.0) The standard deviation of the log normal distribution to accompany the radius mode "LOG NORMAL"
            radius_min: (float, 0.5) The minimum radius of the uniform distribution to accompany the radius mode "UNIFORM" or "LOG_NORMAL"
            radius_max: (float, 1.5) The maximum radius of the uniform distribution to accompany the radius mode "UNIFORM"
            perturbation_scale: (float, 0.5) The scale applied to the calculated positional perturbations.
            subdivisions: (int, 0) The number of subdivisions to create for the Icosphere.
            num_points: (int, 100) The number of points to create on the Fibonacci sphere.
        """

        self._angle_modes = ["RANDOM", "FIBONACCI", "ICOSPHERE"]
        self._radius_modes = ["FIXED", "UNIFORM", "LOG NORMAL"]
        self._perturbations = ["FIXED", "NORMAL", "UNIFORM"]

        angle_mode = angle_mode.upper().strip()
        radius_mode = radius_mode.upper().strip()
        positional_perturbation = positional_perturbation.upper().strip()

        assert angle_mode in self._angle_modes, "You must use a built-in angle mode"
        assert radius_mode in self._radius_modes, "You must use a built-in radius mode"
        assert (
            positional_perturbation in self._perturbations
        ), "You must use a built-in positional perturbation mode"

        self.angle_mode = angle_mode
        self.radius_mode = radius_mode
        self.positional_perturbation = positional_perturbation

        self.perturbation_scale = (
            kwargs["perturbation_scale"] if "perturbation_scale" in kwargs else 0.5
        )

        assert (
            0.00640536 <= fov_x <= 3.01675
        ), "fov_x must be in range [0.00640536, 3.01675]"
        assert (
            0.00640536 <= fov_y <= 3.01675
        ), "fov_y must be in range [0.00640536, 3.01675]"

        self.fov_x = fov_x
        self.fov_y = fov_y

        assert lens >= 1.0, "lens size must be greater than or equal to one millimeter"

        self.lens = lens

        assert (
            sensor_height >= 1.0
        ), "Sensor height must be greater than or equal to one millimeter"
        assert (
            sensor_width >= 1.0
        ), "Sensor width must be greater than or equal to one millimeter"

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

        if "FIBONACCI" in self.angle_mode:
            num_points = kwargs["num_points"] if "num_points" in kwargs else 100
            self._predefined_points = self._generate_fibonacci(num_points)
            print(f"Created {len(self._predefined_points)} predefined points")
            self._angle_selection = kwargs["angle_selection"].upper().strip() if "angle_selection" in kwargs else "RANDOM"
            assert self._angle_selection in ["RANDOM", "ITERATE"], f"Angle mode {self._angle_selection} unsupported."

        elif "ICOSPHERE" in self.angle_mode:
            subdivisions = kwargs["subdivisions"] if "subdivisions" in kwargs else 0
            self._predefined_points = self._generate_icosphere(subdivisions)
            print(f"Created {len(self._predefined_points)} predefined points")
            self._angle_selection = kwargs["angle_selection"].upper().strip() if "angle_selection" in kwargs else "RANDOM"
            assert self._angle_selection in ["RANDOM", "ITERATE"], f"Angle mode {self._angle_selection} unsupported."

        # Determine radii modes
        if "LOG NORMAL" in radius_mode:
            if "radius_mean" in kwargs and "radius_std" in kwargs:
                self._radius_mean, self._radius_std = (
                    kwargs["radius_mean"],
                    kwargs["radius_std"],
                )
            else:
                self._radius_mean, self._radius_std = 0, 1

            if "radius_min" in kwargs:
                self._radius_min = max(0, kwargs["radius_min"])
            else:
                self._radius_min = 0

        if "UNIFORM" in radius_mode:
            if "radius_min" in kwargs and "radius_max" in kwargs:
                self._radius_min, self._radius_max = (
                    max(0, kwargs["radius_min"]),
                    max(0, kwargs["radius_max"]),
                )
            else:
                self._radius_min, self._radius_max = 0.5, 1.5

    def __call__(self, n: int = None):
        # Handle the angle mode
        if self.angle_mode in ["ICOSPHERE", "FIBONACCI"]:

            # Determine how to get the angle 
            if self._angle_selection == "RANDOM":
                theta, phi = random.choice(self._predefined_points)
            else:
                theta, phi = self._predefined_points[n % len(self._predefined_points)]

        elif self.angle_mode == "RANDOM":
            phi = (self.phi_max - self.phi_min) * random.random() + self.phi_min
            theta = (self.theta_max - self.theta_min) * random.random() + self.theta_min

        # Handle the radius mode
        if self.radius_mode == "FIXED":
            radius = self.radius

        elif self.radius_mode == "UNIFORM":
            radius = random.uniform(self._radius_min, self._radius_max)

        elif self.radius_mode == "LOG NORMAL":
            radius = (
                random.lognormvariate(self._radius_mean, self._radius_std)
                + self._radius_min
            )

        # Handle the positional perturbation
        if self.positional_perturbation:

            perturb_range = max(0, self.perturbation_scale * (radius - 1))

            if perturb_range == 0 or self.positional_perturbation == "FIXED":
                perturb_x = perturb_y = perturb_z = 0

            elif self.positional_perturbation == "NORMAL":
                perturb_x, perturb_y, perturb_z = (
                    random.normalvariate(0, perturb_range / 3) for _ in range(3)
                )  # Constrain 99.7% to be within 3 standard deviations

            elif self.positional_perturbation == "UNIFORM":
                perturb_x, perturb_y, perturb_z = (
                    random.uniform(-perturb_range, perturb_range) for _ in range(3)
                )

        blender_string = self._self_to_blend(
            radius, theta, phi, perturb_x, perturb_y, perturb_z
        )

        return blender_string

    def _self_to_blend(self, radius, theta, phi, perturb_x, perturb_y, perturb_z):
        """
        Formats the string to be passed to Blender for rendering
        """

        return f" -r {radius} -tta {theta} -phi {phi} -fovx {self.fov_x} -fovy {self.fov_y} -le {self.lens} -sh {self.sensor_height} -sw {self.sensor_width} -px {perturb_x} -py {perturb_y} -pz {perturb_z}"

    def _cartesian_to_spherical(self, x, y=None, z=None):
        theta = atan(y / (x + 1e-8))
        phi = atan(sqrt(x ** 2 + y ** 2) / (z + 1e-8))

        return theta, phi

    def _fix_angle(self, angle_list: list):
        """
        Check that the supplied angles are within the range specified
        by the user
        """

        return [
            angles
            for angles in angle_list
            if angles[0] >= self.theta_min
            if angles[0] <= self.theta_max
            if angles[1] >= self.phi_min
            if angles[1] <= self.phi_max
        ]

    def _generate_fibonacci(self, n: int = 1):
        GOLDEN_ANGLE = (3 - sqrt(5)) * pi

        angles = [GOLDEN_ANGLE * i for i in range(n)]

        z = [i / n for i in range(1 - n, n, 2)]

        radii = [sqrt(1 - p ** 2) for p in z]

        x = [r * cos(a) for r, a in zip(radii, angles)]
        y = [r * sin(a) for r, a in zip(radii, angles)]

        verts = list(zip(x, y, z))
        verts = [self._cartesian_to_spherical(*v) for v in verts]
        verts = self._fix_angle(list(verts))
        return verts

    def _generate_icosphere(self, subdivisions: int = 0):
        """ Copied from: https://sinestesia.co/blog/tutorials/python-icospheres/ """
        if subdivisions > 4:
            import warnings

            warnings.warn(
                "Using a number of subdivisions greater than four may crash the program"
            )

        middle_point_cache = {}

        PHI = (1 + sqrt(5)) / 2

        def vertex(x, y, z):
            length = sqrt(x ** 2 + y ** 2 + z ** 2)

            return [i / length for i in (x, y, z)]

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
        verts = [self._cartesian_to_spherical(*v) for v in verts]
        verts = self._fix_angle(verts)

        return verts
