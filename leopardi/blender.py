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

# Create the CLI via argparser
argv = sys.argv[sys.argv.index("--") + 1 :]
parser = argparse.ArgumentParser(prog="renderer", description="Blender renderer")
parser.add_argument("-l", dest="labels", type=str, default=None)
parser.add_argument("-rd", dest="render_directory", type=str, default="./renders")
parser.add_argument("-r", dest="radius", type=float, default=1.0)
parser.add_argument("-phi", dest="phi", type=float, default=0.0)
parser.add_argument("-tta", dest="theta", type=float, default=0.0)
parser.add_argument("-wd", dest="work_directory", type=str, required=True)
parser.add_argument("-s", dest="shadow", action="store_true")
parser.add_argument("-rc", dest="render_count", type=int, default=0)
parser.add_argument("-is", dest="image_size", type=int, default=1024)

# model-related arguments
parser.add_argument("-md", dest="model_directory", type=str, default="/models")
parser.add_argument(
    "-mm", dest="model_mode", choices=["iterate", "random"], default="iterate"
)

# background-related arguments
parser.add_argument(
    "-bd", dest="background_directory", type=str, default="/backgrounds"
)
parser.add_argument(
    "-bm", dest="background_mode", choices=["iterate", "random"], default="iterate"
)


args = parser.parse_known_args(argv)[0]


bpy.ops.wm.read_factory_settings(use_empty=True)


# Load in a model
if args.model_mode is "iterate":
    models_list = [
        folder for folder in os.listdir(args.work_directory + args.model_directory)
    ]
    model_folder = models_list[(args.render_count - 1) % len(models_list)]
    model = [
        f
        for f in os.listdir(
            args.work_directory + args.model_directory + "/" + model_folder
        )
        if f[-4:] in [".obj", ".fbx"]
    ][0]

bpy.ops.import_scene.fbx(
    filepath=args.work_directory
    + args.model_directory
    + "/"
    + model_folder
    + "/"
    + model
)

# Select all objects and scale to 2^3 cube centered
# about the origin
minx, miny, minz, maxx, maxy, maxz = (0.0 for _ in range(6))

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

# Set the background of the scene as transparent
bpy.context.scene.render.film_transparent = True

if args.shadow:
    # Get the object's lower z bound to attach the plane to
    min_z = float("inf")
    for p in bpy.context.scene.objects[model[:-4]].bound_box:
        if p[-1] < min_z:
            min_z = p[-1]

    # Add the image shadow
    bpy.ops.mesh.primitive_plane_add(
        enter_editmode=False,
        align="WORLD",
        location=(0, 0, min_z + bpy.context.scene.objects[model[:-4]].location[-1]),
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

# Set the render size
bpy.context.scene.render.resolution_x = args.image_size
bpy.context.scene.render.resolution_y = args.image_size

# Render the final image

#####################################
# TODO: Update with other image sizes
#####################################

bpy.context.scene.render.filepath = (
    args.work_directory
    + args.render_directory
    + "/render_"
    + str(args.render_count).zfill(8)
    + ".jpg"
)

bpy.ops.render.render(write_still=True)
