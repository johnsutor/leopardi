import setuptools

with open("README.md", "r") as f:
    description = f.read()

setuptools.setup(
    name="leopardi",
    version="0.2.2",
    author="John Sutor",
    author_email="johnsutor3@gmail.com",
    description="An extensible library for generating 3D synthetic data with Blender that just works.",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/johnsutor/leopardi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    install_requires=[
        'joblib',
        'Pillow'
    ],
    keywords='synthetic data blender 3d machine learning rendering images yolo coco pascal voc',
    project_urls={
        'Homepage': 'https://github.com/johnsutor/leopardi',
    },
)