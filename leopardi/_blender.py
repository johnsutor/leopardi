"""
Author: John Sutor
Date: May 7th, 2020

This script is executed from within the Blender environment.
It communicates with the Leopardi library via an argument
parser, and is able to efficiently and quickly produce renders
based on the arguments specified.
"""

import math
import sys
import argparse
import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1 :]
parser = argparse.ArgumentParser(prog="renderer", description="Blender renderer")
parser.add_argument(
    "-l",
    dest="labels",
    type=str,
    default=None,
    nargs="*",
    choices=["YOLO", "COCO", "PASCAL", "DEPTH", "MASK"],
)
parser.add_argument(
    "-lt",
    dest="lighting_type",
    type=str,
    required=True,
    default="SUN",
    choices=["SPOT", "SUN", "POINT", "AREA", "FLASHLIGHT"],
)
parser.add_argument("-m", dest="model", type=str, required=True)
# parser.add_argument("-b", dest="background", type=str, required=True)
parser.add_argument("-wd", dest="work_directory", type=str, required=True)
parser.add_argument("-s", dest="shadow", action="store_true")
parser.add_argument("-as", dest="autoscale", action="store_true")
parser.add_argument("-rc", dest="render_count", type=int, default=0)
parser.add_argument("-rd", dest="render_directory", type=str, required=True)
parser.add_argument(
    "-re",
    dest="render_engine",
    type=str,
    default="BLENDER_EEVEE",
    choices=["BLENDER_EEVEE", "CYCLES"],
)
parser.add_argument("-rx", dest="resolution_x", type=int, default=1024)
parser.add_argument("-ry", dest="resolution_y", type=int, default=1024)

# Camera-related arguments
parser.add_argument("-r", dest="radius", type=float, default=1.0)
parser.add_argument("-phi", dest="phi", type=float, default=0.0)
parser.add_argument("-tta", dest="theta", type=float, default=0.0)
parser.add_argument("-fovx", dest="fov_x", type=float, default=0.00640536)
parser.add_argument("-fovy", dest="fov_y", type=float, default=0.00640536)
parser.add_argument("-le", dest="lens", type=float, default=50.0)
parser.add_argument("-sh", dest="sensor_height", type=float, default=24.0)
parser.add_argument("-sw", dest="sensor_width", type=float, default=36.0)
parser.add_argument("-px", dest="perturbation_x", type=float, default=0),
parser.add_argument("-py", dest="perturbation_y", type=float, default=0),
parser.add_argument("-pz", dest="perturbation_z", type=float, default=0),

args = parser.parse_known_args(argv)[0]
print(args)

bpy.ops.wm.read_factory_settings(use_empty=True)

# Set the render size
bpy.context.scene.render.resolution_x = args.resolution_x
bpy.context.scene.render.resolution_y = args.resolution_y

if args.model.endswith('.fbx'):
    bpy.ops.import_scene.fbx(filepath=args.model)
elif args.model.endswith('.obj'):
    bpy.ops.import_scene.fbx(filepath=args.model)

if args.autoscale:
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
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action="DESELECT")

# Convert the spherical coordinates to Cartesian coordinates
x = args.radius * math.sin(args.phi) * math.cos(args.theta) + args.perturbation_x
y = args.radius * math.sin(args.phi) * math.sin(args.theta) + args.perturbation_y
z = args.radius * math.cos(args.phi) + args.perturbation_z

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


# Add the lighting options
if args.lighting_type == "SUN":
    light = bpy.data.lights.new(name="Light", type="SUN")
    light.energy = 2
    light_obj = bpy.data.objects.new("Light", light)
    light_obj.location = (x, y, float("inf"))
    bpy.context.collection.objects.link(light_obj)
    bpy.context.view_layer.objects.active = light_obj

elif args.lighting_type == "SPOT":
    light = bpy.data.lights.new(name="Light", type="SPOT")
    light_obj = bpy.data.objects.new("Light", light)
    light_obj.location = (x, y, z)

    # Calculate direction to rotate the light
    rotation = Vector((x, y, z)).to_track_quat("Z", "Y")
    light_obj.rotation_euler = (
        rotation.to_euler()
    )  # (args.phi, 0.0, args.theta + math.pi / 2)

    bpy.context.collection.objects.link(light_obj)
    bpy.context.view_layer.objects.active = light_obj

elif args.lighting_type == "POINT":
    light = bpy.data.lights.new(name="Light", type="POINT")
    light_obj = bpy.data.objects.new("Light", light)
    light_obj.location = (x, y, z)
    bpy.context.collection.objects.link(light_obj)
    bpy.context.view_layer.objects.active = light_obj

elif args.lighting_type == "AREA":
    light = bpy.data.lights.new(name="Light", type="AREA")
    light_obj = bpy.data.objects.new("Light", light)
    light_obj.location = (x, y, z)

    # Calculate direction to rotate the light
    rotation = Vector((x, y, z)).to_track_quat("Z", "Y")
    light_obj.rotation_euler = rotation.to_euler()

    bpy.context.collection.objects.link(light_obj)
    bpy.context.view_layer.objects.active = light_obj

elif args.lighting_type == "FLASHLIGHT":
    light_out = bpy.data.lights.new(name="Light", type="SPOT")
    light_in = bpy.data.lights.new(name="Light", type="SPOT")

    light_out.spot_size = math.pi / 12
    light_in.spot_size = math.pi / 24
    light_in.energy = 10 * light_in.energy

    # Calculate direction to rotate the light
    rotation = Vector((x, y, z)).to_track_quat("Z", "Y")

    light_obj_out = bpy.data.objects.new("Light", light_out)
    light_obj_out.location = (x, y, z)
    light_obj_out.rotation_euler = rotation.to_euler()
    light_obj_in = bpy.data.objects.new("Light", light_in)
    light_obj_in.location = (x, y, z)
    light_obj_in.rotation_euler = rotation.to_euler()

    bpy.context.collection.objects.link(light_obj_out)
    bpy.context.view_layer.objects.active = light_obj_out
    bpy.context.collection.objects.link(light_obj_in)
    bpy.context.view_layer.objects.active = light_obj_in

bpy.context.scene.render.film_transparent = True


# Labeling
if args.labels:
    if "YOLO" in args.labels:
        bound_low_x, bound_high_x, bound_low_y, bound_high_y = (
            float("inf"),
            -float("inf"),
            float("inf"),
            -float("inf"),
        )

        def clamp(x, minimum, maximum):
            return max(minimum, min(x, maximum))

        def camera_view_bounds_2d(scene, cam_ob, me_ob):
            """
            Returns camera space bounding box of mesh object.

            Negative 'z' value means the point is behind the camera.

            Takes shift-x/y, lens angle and sensor size into account
            as well as perspective/ortho projections.

            :arg scene: Scene to use for frame size.
            :type scene: :class:`bpy.types.Scene`
            :arg obj: Camera object.
            :type obj: :class:`bpy.types.Object`
            :arg me: Untransformed Mesh.
            :type me: :class:`bpy.types.Mesh´
            :return: a Box object (call its to_tuple() method to get x, y, width and height)
            :rtype: :class:`Box`
            """

            mat = cam_ob.matrix_world.normalized().inverted()
            depsgraph = bpy.context.evaluated_depsgraph_get()
            mesh_eval = me_ob.evaluated_get(depsgraph)
            me = mesh_eval.to_mesh()
            me.transform(me_ob.matrix_world)
            me.transform(mat)

            camera = cam_ob.data
            frame = [-v for v in camera.view_frame(scene=scene)[:3]]
            camera_persp = camera.type != "ORTHO"

            lx = []
            ly = []

            for v in me.vertices:
                co_local = v.co
                z = -co_local.z

                if camera_persp:
                    if z == 0.0:
                        lx.append(0.5)
                        ly.append(0.5)
                    # Does it make any sense to drop these?
                    if z <= 0.0:
                        continue
                    else:
                        frame = [(v / (v.z / z)) for v in frame]

                min_x, max_x = frame[1].x, frame[2].x
                min_y, max_y = frame[0].y, frame[1].y

                x = (co_local.x - min_x) / (max_x - min_x)
                y = (co_local.y - min_y) / (max_y - min_y)

                lx.append(x)
                ly.append(y)

            if len(lx) > 0 and len(ly) > 0:
                min_x = clamp(min(lx), 0.0, 1.0)
                max_x = clamp(max(lx), 0.0, 1.0)
                min_y = clamp(min(ly), 0.0, 1.0)
                max_y = clamp(max(ly), 0.0, 1.0)

                mesh_eval.to_mesh_clear()

                return (min_x, max_x, min_y, max_y)

            else:
                mesh_eval.to_mesh_clear()
                return bound_low_x, bound_high_x, bound_low_y, bound_high_y

        for object in bpy.context.scene.objects:
            if object.type == "MESH":
                min_x, max_x, min_y, max_y = camera_view_bounds_2d(
                    bpy.context.scene, bpy.context.scene.camera, object
                )
                if min_x < bound_low_x:
                    bound_low_x = min_x
                if max_x > bound_high_x:
                    bound_high_x = max_x
                if min_y < bound_low_y:
                    bound_low_y = min_y
                if max_y > bound_high_y:
                    bound_high_y = max_y
        # xlist, ylist = [], []

        # # Print all vertices
        # for object in bpy.context.scene.objects:
        #     if object.type == 'MESH':
        #         for v in object.bound_box:
        #             coord = object.matrix_world @ Vector(v)

        #             # Get the location on the final rendered image
        #             img_loc = bpy_extras.object_utils.world_to_camera_view(
        #                 bpy.context.scene, camera_obj, coord
        #             )

        #             print(coord)
        #             print(img_loc)

        #             xlist.append(img_loc.x)
        #             ylist.append(img_loc.y)

        #         # Choose the bounding coordinates
        #         low_x = 0.0 if min(xlist) < 0.0 else 1.0 if min(xlist) > 1.0 else min(xlist)
        #         high_x = 0.0 if max(xlist) < 0.0 else 1.0 if max(xlist) > 1.0 else max(xlist)
        #         low_y = 0.0 if min(ylist) < 0.0 else 1.0 if min(ylist) > 1.0 else min(ylist)
        #         high_y = 0.0 if max(ylist) < 0.0 else 1.0 if max(ylist) > 1.0 else max(ylist)

        # Output coordinates YOLO format
        with open(
            args.render_directory
            + "/render_"
            + str(args.render_count).zfill(8)
            + ".txt",
            "w",
        ) as f:
            f.write(
                f"0 {str((bound_high_x - bound_low_x)/2 + bound_low_x)} {str(1 - ((bound_high_y - bound_low_y)/2 + bound_low_y))} {str(bound_high_x - bound_low_x)} {str(bound_high_y - bound_low_y)}"
            )

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
            args.render_directory + "/depth_" + str(args.render_count).zfill(8) + ".jpg"
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
    args.render_directory + "/render_" + str(args.render_count).zfill(8) + ".jpg"
)

bpy.ops.render.render(write_still=True)
