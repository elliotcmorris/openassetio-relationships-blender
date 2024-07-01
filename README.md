# OpenAsssetio Relationships
A short and to the point demonstration of openassetio relationships, using blender as a demonstration harness

This repo is setup mostly to run the demo, although the scripts are
provided outside of the blendfile in the `scripts` directory, as
they may serve as some reference.

You probably won't get much out of this from a text description, but luckily there
is a video :  https://youtu.be/Ry1xJV906Qo

# Setup
- Clone the repo (From now on, assume commands are run from the repo root directory)
- Extract the "assets.zip" folder, this will create a "Buildings" directory.
- Navigate to your blender install, you will need to install some libraries
  to your blender python environment. This can be found (at time of writing)
  at `Blender-install-dir/3.4/python/bin`
- Install pip, which doesn't come with Blender by default, `./Blender-install-dir/3.4/python/bin/python3.10 -m ensurepip`
- Install the openassetio requirements into the blender python environment `./Blender-install-dir/3.4/python/bin/python3.10 -m pip install -r requirements.txt`
- Configure openassetio to use the provided config file `export OPENASSETIO_DEFAULT_CONFIG="./blender_resolver_config.toml"`
- Launch Blender `./Blender-install-dir/blender`
- Inside blender, open `relationshipScene.blend`
- Navigate to the scripting view if not already open. Near the top of the
  text editor UI, open `openassetio_import.py` and push the "run script" button. (It
  looks like a play button.) Do the same with `object_relationships.py`

This enables the import panel in the scene settings, and the relationships
panel in the object settings of a selected object.

The basic idea here for the demo flow is to import an openasetio object
via the import panel. Blender then persists the entity reference in the
object data. Selecting the object allows the user to then replace the
object with other entities that are related to it via the Proxy relationship trait.
