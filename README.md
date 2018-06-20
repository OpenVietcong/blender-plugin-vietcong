# Blender plugins for Vietcong graphical files

This projects aims to support 3D files used by Vietcong in [Blender](https://www.blender.org/).
Information about the BES format are shared with
[VC-Browser](https://github.com/sonicpp/VC-Browser) project (specifically the 
[doc/bes.md](https://github.com/sonicpp/VC-Browser/blob/master/doc/bes.md)
document).
See also the official topic at
[vietcong.info](http://www.vietcong.info/portal/forum/viewthread.php?thread_id=1038).

## Current status
* Importing BES files:
  * vertices/faces
  * model hierarchy

## Planned features
* Importing BES files:
  * textures
  * importing other (currently unknown) information from BES
* Exporting BES files
* Object animations?

## Testing data set
This script was tested on objects made by Gonzo, which are available at [Gonzo's Laboratory](http://vietcong.7x.cz/edit-panel/moje-objekty).
It is planned to extend these test data to objects packed in CBF files (like files in Vietcong installation folder or user made maps).

## Installation
Save import\_bes.py script to your Blender Addons folder:
* for Linux: /usr/share/blender/[version]/scripts/addons
* for Windows:
  * default installation directory: C:\Program Files\Blender Foundation\blender\[version]\addons 
  * user location: C:\Users\[user profile]\AppData\Roaming\Blender Foundation\Blender\[user folder]\scripts\addons

Start Blender and select File -> User Preferences, then enable "Import-Export: Vietcong BES (.bes)" in Import-Export category.
If you want to auto-enable this plugin each time Blender starts, click on "Save User Settings" in the same window.

After that you should see the option File -> Import -> BES (.bes)

