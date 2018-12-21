# Blender plugins for Vietcong graphical files

This projects aims to support 3D files used by Vietcong in [Blender](https://www.blender.org/).
Information about the BES format are shared with
[vc-spec](https://github.com/OpenVietcong/vc-spec)
project (specifically the
[doc/bes.md](https://github.com/OpenVietcong/vc-spec/blob/master/doc/bes.md)
document).
See also the official topic at
[vietcong.info](http://www.vietcong.info/portal/forum/viewthread.php?thread_id=1038).

## Current status
* Importing BES files (version 0100):
  * vertices/faces
  * model hierarchy
  * materials/textures
  * UV mapping

## Planned features
* Importing BES files:
  * Handle special materials like PteroMat/Bitmap and their textures
  * importing other (currently unknown) information from BES
* Exporting BES files

## Possible improvements in distant future
* Other BES verions
* Model animations
* Scenes
* Skelet animations

## Testing data set
This script has been tested on objects made by Gonzo (which are available at
[Gonzo's Laboratory](http://vietcong.7x.cz/edit-panel/moje-objekty))
and BES files extracted from official
[CBF](https://github.com/OpenVietcong/vc-spec/blob/master/doc/cbf.md)
archives bundled with Vietcong 1.60 installation.

It is planned to extend these test data to all user made maps.

## Installation
Save import\_bes.py script to your Blender Addons folder:
* for Linux:
  * system: /usr/share/blender/[version]/scripts/addons
  * user: $HOME/.config/blender/[version]/scripts/addons
* for Mac:
  * system: /Library/Application Support/Blender/[version]/scripts/addons
  * user: /Users/$USER/Library/Application Support/Blender/[version]/scripts/addons
* for Windows:
  * default installation directory: C:\Program Files\Blender Foundation\blender\\[version]\scripts\addons
  * user location: C:\Users\\[user profile]\AppData\Roaming\Blender Foundation\Blender\\[user folder]\scripts\addons

Start Blender and select File -> User Preferences, then enable "Import-Export: Vietcong BES (.bes)" in Import-Export category.
If you want to auto-enable this plugin each time Blender starts, click on "Save User Settings" in the same window.

After that you should see the option File -> Import -> BES (.bes)
In Import file browser you have an opportunity to select additionale directories where import script should look for required texture files.

## Importing BES
* BES contains names of used textures, but not their location.
Import script search for those textures in directory where is imported BES file located,
but user can add more directories where import plugin will look for BES textures.
* Model textures can be splitted over several directories and subdirectories.
To make importing easier to user, script offers the opportunity to enable searching textures recursively in selected directories.
However, this operation may be slow.
* Sometimes texture extension in file system differs with extension from  BES file.
For that case, user can choose whether import plugin will ignore texture extensions or not.
In that case, plugin will search for textures with any supported extension in following order: DDS, TGA, BMP (like PteroEngine does).
* Script will set blend type of textures and alpha transparency of every material and texture the way to be rendered by Blender as close as possible to PteroEngine renderer.

