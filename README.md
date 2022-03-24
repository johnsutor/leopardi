# Leopardi 
*An extensible library for generating 3D synthetic data with Blender that just works.*
Requires Python >= 3.0, Blender >= 2.80
**NEW** Check out our new documentation website [here](https://johnsutor.github.io/leopardi/)

Leopardi aims to make it easy to create robust synthetic images by importing scenes into Blender. It takes care of the boring, strenuous, and difficult stuff so that you can devote your time to training and evaluating your machine learning models.

**NOTE: Leopardi is currently in a pre-alpha change. Breaking changes (though unlikely) may occur.**

## Backgrounds 
Backgrounds are imported from a specified directory (which defaults to ./backgrounds/) and merges them with the rendered image.

## Camera 
The Leopardi Camera extends Blender's default camera with a variety of options for choosing camera location, lens size, sensor size, and more.

## Models 
Similarly to backgrounds, models are imported from a specified directory (which defaults to ./models/) and are used to render a synthetic image.

## Renderer
The renderer allows for specifying which labels to generate to accompany an image, which Blender rendering engine to use, as well as the resolution of the rendered images. 

## Examples
Below is a dead-simple demonstration of working with Leopardi on Windows to generate a single render.

```python
import leopardi

BLENDER_DIR = "C:\Program Files\Blender Foundation\Blender 2.92"

camera = leopardi.LeopardiCamera()
lighting = leopardi.LeopardiLighting()
renderer = leopardi.LeopardiRenderer()
model_loader = leopardi.ModelLoader()
background_loader = leopardi.BackgroundLoader()

engine = leopardi.Leopardi(camera, lighting, renderer, background_loader, model_loader)
engine.render(1)
```

If we want to include a depth map and YOLO annotations with our renders, we do so as below

```python
import leopardi

BLENDER_DIR = "C:\Program Files\Blender Foundation\Blender 2.92"

camera = leopardi.LeopardiCamera()
lighting = leopardi.LeopardiLighting()
renderer = leopardi.LeopardiRenderer(labels=["DEPTH", "YOLO"])
model_loader = leopardi.ModelLoader()
background_loader = leopardi.BackgroundLoader()

engine = leopardi.Leopardi(camera, lighting, renderer, background_loader, model_loader)
engine.render(1)
```
