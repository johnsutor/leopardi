"""
Author: John Sutor
Date: May 7th, 2020

This script is executed from within the Blender environment.
It communicates with the Leopardi library via an argument
parser, and is able to efficiently and quickly produce renders
based on the arguments specified.
"""

import os
import random
import math
import sys
import argparse
import bpy
import bpy_extras
from addon_utils import enable

argv = sys.argv[sys.argv.index("--") + 1 :]
parser = argparse.ArgumentParser(prog="renderer", description="Blender renderer")
parser.add_argument(
    "-l",
    dest="labels",
    type=str,
    default=None,
    nargs="*",
    choices=["YOLO", "COCO", "PASCAL", "DEPTH"],
)
parser.add_argument("-m", dest="model", type=str, required=True)
# parser.add_argument("-b", dest="background", type=str, required=True)
parser.add_argument("-wd", dest="work_directory", type=str, required=True)
parser.add_argument("-s", dest="shadow", action="store_true")
parser.add_argument("-rc", dest="render_count", type=int, default=0)
parser.add_argument("-rd", dest="render_directory", type=str, required=True)
parser.add_argument(
    "-re",
    dest="render_engine",
    type=str,
    default="BLENDER_EEVEE",
    choices=["BLENDER_EEVEE", "CYCLES"],
)
parser.add_argument("-is", dest="image_size", type=int, default=1024)

# Camera-related arguments
parser.add_argument("-r", dest="radius", type=float, default=1.0)
parser.add_argument("-phi", dest="phi", type=float, default=0.0)
parser.add_argument("-tta", dest="theta", type=float, default=0.0)
parser.add_argument("-fovx", dest="fov_x", type=float, default=0.00640536)
parser.add_argument("-fovy", dest="fov_y", type=float, default=0.00640536)
parser.add_argument("-le", dest="lens", type=float, default=50.0)
parser.add_argument("-sh", dest="sensor_height", type=float, default=24.0)
parser.add_argument("-sw", dest="sensor_width", type=float, default=36.0)


args = parser.parse_known_args(argv)[0]
print(args)

bpy.ops.wm.read_factory_settings(use_empty=True)

# Set the render size
bpy.context.scene.render.resolution_x = args.image_size
bpy.context.scene.render.resolution_y = args.image_size

bpy.ops.import_scene.fbx(filepath=args.model)

# Select all objects and scale to 2^3 cube centered
# about the origin
minx, miny, minz, maxx, maxy, maxz = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

for obj in bpy.data.objects.keys():
    for p in bpy.data.objects[obj].bound_box:
        x, y, z = p

        if x < minx:
            minx = x
        elif x > maxx:
            maxx = x

        if y < miny:
            miny = y
        elif y > maxy:
            maxy = y

        if z < minz:
            minz = z
        elif z > maxz:
            maxz = z

xdim = maxx - minx
ydim = maxy - miny
zdim = maxz - minz

scale_factor = 2.0 / max((xdim, ydim, zdim))

bpy.ops.object.select_all(action="SELECT")
bpy.ops.transform.resize(value=(scale_factor, scale_factor, scale_factor))
bpy.ops.object.select_all(action="DESELECT")

# Convert the spherical coordinates to Cartesian coordinates
x = args.radius * math.sin(args.phi) * math.cos(args.theta)
y = args.radius * math.sin(args.phi) * math.sin(args.theta)
z = args.radius * math.cos(args.phi)

# Add a camera
camera = bpy.data.cameras.new("Camera")
camera.angle_x = args.fov_x
camera.angle_y = args.fov_y
camera.lens = args.lens
camera.sensor_height = args.sensor_height
camera.sensor_width = args.sensor_width

# bg_img = bpy.data.images.load(args.background_image)
# camera.data.show_background_images = True
# bg = camera.data.background_images.new()

camera_obj = bpy.data.objects.new("Camera", camera)
camera_obj.location = (x, y, z)
camera_obj.rotation_euler = (args.phi, 0.0, args.theta + math.pi / 2)
bpy.context.scene.camera = camera_obj


# Add the sun
light = bpy.data.lights.new(name="Light", type="SUN")
light.energy = 2
light_obj = bpy.data.objects.new("Light", light)
light_obj.location = (x, y, float("inf"))
bpy.context.collection.objects.link(light_obj)
bpy.context.view_layer.objects.active = light_obj

bpy.context.scene.render.film_transparent = True


# Labeling
if args.labels is not None:
    if "YOLO" in args.labels:
        raise NotImplementedError

    if "COCO" in args.labels:
        raise NotImplementedError

    if "PASCAL" in args.labels:
        raise NotImplementedError

    if "DEPTH" in args.labels:
        bpy.context.scene.use_nodes = True
        node_tree = bpy.context.scene.node_tree
        normalize = node_tree.nodes.new(type="CompositorNodeNormalize")

        node_tree.links.new(node_tree.nodes[1].outputs[2], normalize.inputs[0])
        node_tree.links.new(normalize.outputs[0], node_tree.nodes[0].inputs[0])
        node_tree.links.new(node_tree.nodes[1].outputs[1], node_tree.nodes[0].inputs[1])

        bpy.context.scene.render.filepath = (
            args.render_directory
            + "/depth_"
            + str(args.render_count).zfill(8)
            + ".jpg"
        )

        bpy.ops.render.render(write_still=True)

        # Reset links
        node_tree.links.remove(node_tree.nodes[1].outputs[2].links[0])
        node_tree.links.remove(node_tree.nodes[0].inputs[0].links[0])
        node_tree.links.remove(node_tree.nodes[1].outputs[1].links[0])
        node_tree.links.new(node_tree.nodes[1].outputs[0], node_tree.nodes[0].inputs[0])
        node_tree.links.new(node_tree.nodes[1].outputs[1], node_tree.nodes[0].inputs[1])


if args.shadow:
    # Get the object's lower z bound to attach the plane to
    # Add the image shadow
    bpy.ops.mesh.primitive_plane_add(
        enter_editmode=False,
        align="WORLD",
        location=(0, 0, minz),
    )
    plane = bpy.data.objects["Plane"]

    plane_material = bpy.data.materials.new(name="PlaneMaterial")
    plane_material.use_nodes = True
    plane.data.materials.append(plane_material)

    # Clear all nodes to start
    if plane_material.node_tree:
        plane_material.node_tree.links.clear()
        plane_material.node_tree.nodes.clear()

    # Edit the node tree
    bpy.context.active_object.active_material = plane_material

    node_tree = bpy.context.active_object.active_material.node_tree

    bsdf_diffuse = node_tree.nodes.new(type="ShaderNodeBsdfDiffuse")
    shader_to_rgb = node_tree.nodes.new(type="ShaderNodeShaderToRGB")

    # Link the BSDF Diffuse to the RGB Converter
    node_tree.links.new(bsdf_diffuse.outputs[0], shader_to_rgb.inputs[0])

    color_ramp = node_tree.nodes.new(type="ShaderNodeValToRGB")

    # Link the RGB Converter to the BW Converter
    node_tree.links.new(shader_to_rgb.outputs[0], color_ramp.inputs[0])

    mixer = node_tree.nodes.new(type="ShaderNodeMixShader")
    bsdf_diffuse_2 = node_tree.nodes.new(type="ShaderNodeBsdfDiffuse")
    bsdf_transparent = node_tree.nodes.new(type="ShaderNodeBsdfTransparent")

    # Set the bsdf diffuse to black
    bsdf_diffuse_2.inputs[0].default_value = (0, 0, 0, 1)

    # Link the mixer to the BSDF Transparent and the BW Converter
    node_tree.links.new(color_ramp.outputs[0], mixer.inputs[0])
    node_tree.links.new(bsdf_diffuse_2.outputs[0], mixer.inputs[1])
    node_tree.links.new(bsdf_transparent.outputs[0], mixer.inputs[2])

    # Create an output and link it
    output = node_tree.nodes.new(type="ShaderNodeOutputMaterial")
    node_tree.links.new(mixer.outputs[0], output.inputs[0])

    # Set the blend method for the material
    plane_material.blend_method = "BLEND"

# Render the final image

#####################################
# TODO: Update with other image saving
#####################################

bpy.context.scene.render.engine = args.render_engine
bpy.context.scene.render.filepath = (
    args.render_directory
    + "/render_"
    + str(args.render_count).zfill(8)
    + ".jpg"
)

bpy.ops.render.render(write_still=True)
