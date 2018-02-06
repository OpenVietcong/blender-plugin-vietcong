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

import os
import struct
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, CollectionProperty

bl_info = {
    "name"       : "Vietcong BES (.bes)",
    "author"     : "Jan Havran",
    "version"    : (0, 1),
    "blender"    : (2, 70, 0),
    "location"   : "File > Import > BES (.bes)",
    "description": "Import Vietcong BES files",
    "wiki_url"   : "https://github.com/sonicpp/vietcong-blender-plugins",
    "category"   : "Import-Export",
}

class BES(object):
    vertices = []
    faces = []
    def __init__(self, fname):
        self.f = open(fname, "rb")

        self.read_header()
        self.read_preview()
        self.read_data()

        self.vertices = [(0, 0, 0), (5, 0, 0), (2.5, 5, 0)]
        self.faces = [(0, 1, 2)]

    def parse(self, fmt):
        st_fmt = fmt
        st_len = struct.calcsize(st_fmt)
        st_unpack = struct.Struct(st_fmt).unpack_from
        data = st_unpack(self.f.read(st_len))
        return data

    def read_header(self):
        data = self.parse("<5s4sI3c")
        print(data)

    def read_preview(self):
        self.f.read(0x3000)

    def read_data(self):
        (label, size) = self.parse("<II")
        print("Block {} of size {} bytes".format(hex(label),size))

class BESImporter(bpy.types.Operator, ImportHelper):
    bl_idname = "import_mesh.bes"
    bl_label  = "Import BES files"

    # Show only "*.bes" files for import
    filter_glob = StringProperty(default="*.bes", options={'HIDDEN'})

    # Directory of selected files for import
    directory = StringProperty(options={'HIDDEN'})

    # Collection of selected files for import
    files = CollectionProperty(name="File name", type=bpy.types.OperatorFileListElement)

    def execute(self, context):
        for f in self.files:
            # Create new object
            bes = BES(os.path.join(self.directory, f.name))
            mesh = bpy.data.meshes.new(f.name)
            obj = bpy.data.objects.new(f.name, mesh)

            # Add object into scene
            bpy.context.scene.objects.link(obj)

            # Update mesh data
            mesh.from_pydata(bes.vertices, [], bes.faces)
            mesh.update(calc_edges=True)

            print(os.path.join(self.directory, f.name))

        return {'FINISHED'}

def menu_import_bes(self, context):
    self.layout.operator(BESImporter.bl_idname, text="BES (.bes)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_import_bes)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_import_bes)

if __name__ == "__main__":
    register()

