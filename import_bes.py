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

class BESObject(object):
    def __init__(self, name):
        self.name = name
        self.children = []
        self.meshes = []

class BESMesh(object):
    def __init__(self, mesh_id, vertices, faces):
        self.id = mesh_id
        self.vertices = vertices
        self.faces = faces

class BES(object):
    class BlockID:
        Object     = 0x0001
        Unk30      = 0x0030
        Mesh       = 0x0031
        Vertices   = 0x0032
        Faces      = 0x0033
        Properties = 0x0034
        Unk35      = 0x0035
        Unk36      = 0x0036
        Unk38      = 0x0038
        UserInfo   = 0x0070

    def __init__(self, fname):
        self.objects = []
        self.f = open(fname, "rb")

        self.read_header()
        self.read_preview()
        self.read_data()

    def unpack(self, fmt, data):
        st_fmt = fmt
        st_len = struct.calcsize(st_fmt)
        st_unpack = struct.Struct(st_fmt).unpack_from
        return st_unpack(data[:st_len])

    def read_header(self):
        data = self.f.read(0x10)
        print(self.unpack("<5s4sI3c", data))

    def read_preview(self):
        self.f.read(0x3000)

    def read_data(self):
        data = self.f.read()
        self.parse_data(data)

    def parse_data(self, data):
        start = 0
        while (len(data[start:]) > 8):
            (label, size) = self.parse_block_header(data[start:])
            print("Block {} of size {} bytes".format(hex(label),size))
            subblock = data[start+8:start+size]
            start += size 

            if   label == BES.BlockID.Object:
                self.objects.append(self.parse_block_object(subblock))
            elif label == BES.BlockID.Unk30:
                self.parse_block_unk30(subblock)
            elif label == BES.BlockID.Mesh:
                self.parse_block_mesh(subblock)
            elif label == BES.BlockID.Vertices:
                self.parse_block_vertices(subblock)
            elif label == BES.BlockID.Faces:
                self.parse_block_faces(subblock)
            elif label == BES.BlockID.Properties:
                self.parse_block_properties(subblock)
            elif label == BES.BlockID.Unk35:
                self.parse_block_unk35(subblock)
            elif label == BES.BlockID.Unk36:
                self.parse_block_unk36(subblock)
            elif label == BES.BlockID.Unk38:
                self.parse_block_unk38(subblock)
            elif label == BES.BlockID.UserInfo:
                self.parse_block_user_info(subblock)
            elif label == 0x100:
                self.parse_block_unk100(subblock)
            else:
                print("Unknown block {}".format(hex(label)))

    def parse_block_header(self, data):
        return self.unpack("<II", data)

    def parse_block_object(self, data):
        (children, name_size) = self.unpack("<II", data)
        (name,) = self.unpack("<" + str(name_size) + "s", data[8:])
        name = str(name, 'ascii').strip(chr(0))

        model = BESObject(name)
        print("Children: {}, Name({}): {}".format(children, name_size, name))

        start = 8 + name_size
        while len(data[start:]) > 0:
            (label, size) = self.parse_block_header(data[start:])
            subblock = data[start+8:start+size]
            start += size

            if label == BES.BlockID.Object:
                model.children.append(self.parse_block_object(subblock))
            elif label == BES.BlockID.Unk30:
                model.meshes = self.parse_block_unk30(subblock)

        return model

    def parse_block_unk30(self, data):
        (mesh_children,) = self.unpack("<I", data)
        meshes = []

        start = 4
        while len(data[start:]) > 0:
            (label, size) = self.parse_block_header(data[start:])
            subblock = data[start+8:start+size]
            start += size

            if label == BES.BlockID.Mesh:
                meshes.append(self.parse_block_mesh(subblock))

        return meshes

    def parse_block_mesh(self, data):
        (mesh_id,) = self.unpack("<I", data)
        vertices = None
        faces = None

        start = 4
        while len(data[start:]) > 0:
            (label, size) = self.parse_block_header(data[start:])
            subblock = data[start+8:start+size]
            start += size

            if label == BES.BlockID.Vertices:
                if vertices:
                    print("Multiple vertices blocks in single mesh")
                    return
                vertices = self.parse_block_vertices(subblock)
            elif label == BES.BlockID.Faces:
                if faces:
                    print("Multiple face blocks in single mesh")
                    return
                faces = self.parse_block_faces(subblock)
            else:
                print("Invalid block in mesh")
                return

        mesh = BESMesh(mesh_id, vertices, faces)
        return mesh

    def parse_block_vertices(self, data):
        (count, size, unknown) = self.unpack("<III", data)
        vertices = []

        if size < 12:
            print("Unsupported size '{}' of vertex struct".format(size))
            return
        if count * size != len(data[12:]):
            print("Block size mismatch")
            return

        ptr = 12
        for i in range(count):
            (x,y,z, unk) = self.unpack("<fff" + str(size-12) + "s", data[ptr:])
            vertices.append((x,y,z))
            ptr += size

        return vertices

    def parse_block_faces(self, data):
        (count,) = self.unpack("<I", data)
        faces = []

        if count * 12 != len(data[4:]):
            print("Block size mismatch")
            return

        ptr = 4
        for i in range(count):
            (a, b, c) = self.unpack("<III", data[ptr:])
            faces.append((a,b,c))
            ptr += 12

        return faces

    def parse_block_properties(self, data):
        pass
    def parse_block_unk35(self, data):
        pass
    def parse_block_unk36(self, data):
        pass
    def parse_block_unk38(self, data):
        pass
    def parse_block_user_info(self, data):
        pass
    def parse_block_unk100(self, data):
        pass

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
        # Load all selected files
        for f in self.files:
            # Parse BES file
            bes = BES(os.path.join(self.directory, f.name))

            # Parse all objects in BES file
            for bes_obj in bes.objects:
                self.add_object(bes_obj, None)

        return {'FINISHED'}

    def add_object(self, bes_obj, parent):
        # Create new object
        bpy_obj = bpy.data.objects.new(bes_obj.name, None)
        bpy_obj.parent = parent

        # Since Blender does not allow multiple meshes for single object (while BES does),
        # we have to create seperate object for every mesh.
        for bes_mesh in bes_obj.meshes:
            # In BES the meshes do not have names, so we create one from object name and mesh ID
            mesh_name = "{}.{:08X}".format(bes_obj.name, bes_mesh.id)

            # Create new mesh
            bpy_mesh = bpy.data.meshes.new(mesh_name)

            # Update mesh data
            bpy_mesh.from_pydata(bes_mesh.vertices, [], bes_mesh.faces)
            bpy_mesh.update(calc_edges = True)

            # Create new object from mesh and add it into scene
            mesh_obj = bpy.data.objects.new(mesh_name, bpy_mesh)
            mesh_obj.parent = bpy_obj
            bpy.context.scene.objects.link(mesh_obj)

        # Add children
        for bes_child in bes_obj.children:
            self.add_object(bes_child, bpy_obj)

        # Add object into scene
        bpy.context.scene.objects.link(bpy_obj)

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

