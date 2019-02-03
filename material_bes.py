# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  version 2 as published by the Free Software Foundation.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy

bl_info = {
    "name"       : "Vietcong BES",
    "author"     : "Jan Havran",
    "version"    : (0, 1),
    "blender"    : (2, 79, 0),
    "location"   : "Properties > Material",
    "description": "Vietcong BES Material Tools",
    "wiki_url"   : "https://github.com/OpenVietcong/blender-plugin-vietcong",
    "tracker_url": "https://github.com/OpenVietcong/blender-plugin-vietcong/issues",
    "category"   : "Material",
}

class ptero_material(bpy.types.Panel):
    bl_idname = "material.bes"
    bl_label = "BES Materials"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    def draw(self, context):
        pass

def register():
    bpy.utils.register_class(ptero_material)

def unregister():
    bpy.utils.unregister_class(ptero_material)

if __name__ == "__main__":
    register()

