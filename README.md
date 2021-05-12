# Leopardi 
### Alpha 
*An extensible library for generating 3D synthetic data with Blender that just works.*

Leopardi aims to make it easy to create robust synthetic images by importing scenes into Blender. It takes care of the boring, strenuous, and difficult stuff so that you can devote your time to training and evaluating your machine learning models.

## Backgrounds 
Backgrounds are imported from a speficied directory (which defaults to ./backgrounds/) and merges them with the rendered image.

## Camera 
The Leopardi Camera extends Blender's default camera with a variety of options for choosing camera location, lens size, sensor size, and more.

## Models 
Similarly to backgrounds, models are imported from a specified directory (which defaults to ./models/) and are used to render a synthetic image.

## Renderer
The renderer allows for specifying which labels to generate to accompany an image, which Blender rendering engine to use, as well as the resolution of the rendered images. 