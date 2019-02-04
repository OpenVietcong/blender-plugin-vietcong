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

class BESMaterialProperties(bpy.types.PropertyGroup):
    material_type = bpy.props.EnumProperty(
        name = "Material",
        description = "BES material type",
        items = [
            ("Standard", "Standard", "Standard 3DS Max material"),
            ("PteroMat", "PteroMat", "Ptero-Engine II Material"),
        ],
    )

class BESMaterial(bpy.types.Panel):
    bl_idname = "material.bes"
    bl_label = "BES Materials"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return bpy.context.active_object and bpy.context.active_object.active_material

    def draw(self, context):
        layout = self.layout
        layout.prop(context.active_object.active_material.bes_mat_panel, "material_type")

def register():
    bpy.utils.register_class(BESMaterial)
    bpy.utils.register_class(BESMaterialProperties)
    bpy.types.Material.bes_mat_panel = bpy.props.PointerProperty(type=BESMaterialProperties)

def unregister():
    del bpy.types.Material.bes_mat_panel
    bpy.utils.unregister_class(BESMaterialProperties)
    bpy.utils.unregister_class(BESMaterial)

if __name__ == "__main__":
    register()

