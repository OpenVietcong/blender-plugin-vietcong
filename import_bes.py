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

class BESError(Exception):
    def __init__(self, msg):
        self.msg = msg
        Exception.__init__(self, msg)

class BESObject(object):
    def __init__(self, name):
        self.name = name
        self.children = []
        self.meshes = []
        self.materials = []
        self.position = (0.0, 0.0, 0.0)

class BESMesh(object):
    def __init__(self, vertices, faces, material):
        self.vertices = vertices
        self.faces = faces
        self.material = material

class BESMaterial(object):
    NoneMaterial = 0xFFFFFFFF

    def __init__(self):
        pass

class BESBitmap(BESMaterial):
    def __init__(self):
        pass

class BESPteroMat(BESMaterial):
    def __init__(self, name):
        self.name = name

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
        Material   = 0x1000
        Bitmap     = 0x1001
        PteroMat   = 0x1002

    class BlockPresence:
        OptSingle   = 0  # <0;1>
        OptMultiple = 1  # <0;N>
        ReqSingle   = 2  # <1;1>
        ReqMultiple = 3  # <1;N>

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
        self.unpack("<5s4sI3c", data)

    def read_preview(self):
        self.f.read(0x3000)

    def read_data(self):
        data = self.f.read()
        self.parse_data(data)

    def parse_data(self, data):
        try:
            res = self.parse_blocks({BES.BlockID.UserInfo : BES.BlockPresence.ReqSingle,
                                     BES.BlockID.Object   : BES.BlockPresence.ReqSingle},
                                    data)
            self.objects.append(res[BES.BlockID.Object])
        except BESError as e:
            print(e.msg)
            print("Please report an issue at https://github.com/sonicpp/vietcong-blender-plugins/issues")

    def parse_block_desc(self, data):
        return self.unpack("<II", data)

    def parse_block_by_label(self, label, data):
        try:
            if   label == BES.BlockID.Object:
                return self.parse_block_object(data)
            elif label == BES.BlockID.Unk30:
                return self.parse_block_unk30(data)
            elif label == BES.BlockID.Mesh:
                return self.parse_block_mesh(data)
            elif label == BES.BlockID.Vertices:
                return self.parse_block_vertices(data)
            elif label == BES.BlockID.Faces:
                return self.parse_block_faces(data)
            elif label == BES.BlockID.Properties:
                return self.parse_block_properties(data)
            elif label == BES.BlockID.Unk35:
                return self.parse_block_unk35(data)
            elif label == BES.BlockID.Unk36:
                return self.parse_block_unk36(data)
            elif label == BES.BlockID.Unk38:
                return self.parse_block_unk38(data)
            elif label == BES.BlockID.UserInfo:
                return self.parse_block_user_info(data)
            elif label == BES.BlockID.Material:
                return self.parse_block_material(data)
            elif label == BES.BlockID.Bitmap:
                return self.parse_block_bitmap(data)
            elif label == BES.BlockID.PteroMat:
                return self.parse_block_pteromat(data)
            else:
                raise BESError("Unknown block")
        except BESError as e:
            raise BESError("{:04X}->{}".format(label, e.msg))

    def parse_blocks(self, blocks, data):
        # Init return values
        ret = dict()
        for label in blocks:
            if blocks[label] == BES.BlockPresence.OptSingle or blocks[label] == BES.BlockPresence.ReqSingle:
                ret[label] = None
            else:
                ret[label] = []

        # Search for all blocks
        start = 0
        while len(data[start:]) > 0:
            (label, size) = self.parse_block_desc(data[start:])

            if label in blocks:
                subblock = data[start + 8: start + size]

                if blocks[label] == BES.BlockPresence.OptSingle or blocks[label] == BES.BlockPresence.ReqSingle:
                    blocks.pop(label)
                    ret[label] = self.parse_block_by_label(label, subblock)
                else:
                    ret[label].append(self.parse_block_by_label(label, subblock))
            else:
                raise BESError("Unexpected block {:04X} in this location".format(label))
            start += size

        if start != len(data):
            raise BESError("Block contains more data than expected")

        # Check if all required blocks were found in this block
        for label in blocks:
            if blocks[label] == BES.BlockPresence.ReqSingle:
                raise BESError("Required block {:04X} not found in this location".format(label))
            elif blocks[label] == BES.BlockPresence.ReqMultiple and label not in ret:
                raise BESError("Required block {:04X} not found in this location".format(label))

        return ret

    def parse_block_object(self, data):
        (children, name_size) = self.unpack("<II", data)
        (name,) = self.unpack("<" + str(name_size) + "s", data[8:])
        name = str(name, 'ascii').strip(chr(0))

        model = BESObject(name)

        res = self.parse_blocks({BES.BlockID.Object     : BES.BlockPresence.OptMultiple,
                                 BES.BlockID.Properties : BES.BlockPresence.OptSingle,
                                 BES.BlockID.Unk30      : BES.BlockPresence.OptSingle,
                                 BES.BlockID.Unk35      : BES.BlockPresence.OptSingle,
                                 BES.BlockID.Unk38      : BES.BlockPresence.OptSingle,
                                 BES.BlockID.Material   : BES.BlockPresence.OptSingle},
                                data[8 + name_size:])

        for obj in res[BES.BlockID.Object]:
            model.children.append(obj)
        if res[BES.BlockID.Unk35]:
            model.position = res[BES.BlockID.Unk35]
        if res[BES.BlockID.Unk30]:
            if res[BES.BlockID.Unk30][BES.BlockID.Mesh]:
                model.meshes = res[BES.BlockID.Unk30][BES.BlockID.Mesh]
            if res[BES.BlockID.Unk30][BES.BlockID.Unk35]:
                model.position = res[BES.BlockID.Unk30][BES.BlockID.Unk35]
        if res[BES.BlockID.Material]:
            model.materials = res[BES.BlockID.Material]
            # TODO check all children meshes for valid materials

        return model

    def parse_block_unk30(self, data):
        (mesh_children,) = self.unpack("<I", data)

        res = self.parse_blocks({BES.BlockID.Mesh      : BES.BlockPresence.OptMultiple,
                                 BES.BlockID.Properties: BES.BlockPresence.ReqSingle,
                                 BES.BlockID.Unk35     : BES.BlockPresence.ReqSingle,
                                 BES.BlockID.Unk36     : BES.BlockPresence.OptSingle},
                                data[4:])

        if mesh_children != len(res[BES.BlockID.Mesh]):
            raise BESError("Number of meshes does not match")

        return res

    def parse_block_mesh(self, data):
        """ Parse Mesh block and return BESMesh instance """
        (material,) = self.unpack("<I", data)
        vertices = None
        faces = None

        res = self.parse_blocks({BES.BlockID.Vertices  : BES.BlockPresence.ReqSingle,
                                 BES.BlockID.Faces     : BES.BlockPresence.ReqSingle},
                                data[4:])
        vertices = res[BES.BlockID.Vertices]
        faces    = res[BES.BlockID.Faces]

        if max(max(faces, key=lambda item:item[1])) > len(vertices):
            raise BESError("Invalid faces number")

        return BESMesh(vertices, faces, material)

    def parse_block_vertices(self, data):
        """
        Parse Vertices block and return list of tuples.
        Each tuple means one vertex made of 3 floats (coordinates x, y, z)
        """
        (count, size, unknown) = self.unpack("<III", data)
        vertices = []

        if size < 12:
            raise BESError("Unsupported size '{}' of vertex struct".format(size))
        if count * size != len(data[12:]):
            raise BESError("Block size mismatch")

        ptr = 12
        for i in range(count):
            (x,y,z, unk) = self.unpack("<fff" + str(size-12) + "s", data[ptr:])
            vertices.append((x,y,z))
            ptr += size

        return vertices

    def parse_block_faces(self, data):
        """
        Parse Faces block and return list of tuples.
        Each tuple means one face made of 3 integers (vertices IDs)
        """
        (count,) = self.unpack("<I", data)
        faces = []

        if count * 12 != len(data[4:]):
            raise BESError("Block size mismatch")

        ptr = 4
        for i in range(count):
            (a, b, c) = self.unpack("<III", data[ptr:])
            faces.append((a,b,c))
            ptr += 12

        return faces

    def parse_block_properties(self, data):
        pass

    def parse_block_unk35(self, data):
        """ Parse Unk35 block and return object position as tuple (coordinates x, y, z) """
        if len(data) != 100:
            raise BESError("Block size mismatch")

        return self.unpack("<fff", data)

    def parse_block_unk36(self, data):
        pass
    def parse_block_unk38(self, data):
        pass
    def parse_block_user_info(self, data):
        pass

    def parse_block_material(self, data):
        (materialCnt,) = self.unpack("<I", data)

        res = self.parse_blocks({BES.BlockID.Bitmap     : BES.BlockPresence.OptMultiple,
                                 BES.BlockID.PteroMat   : BES.BlockPresence.OptMultiple},
                                data[4:])

        return res[BES.BlockID.PteroMat]

    def parse_block_bitmap(self, data):
        (unk1, unk2, bitmaps) = self.unpack("<I4sI", data)

        material = BESBitmap()
        return material

    def parse_block_pteromat(self, data):
        (sides, materials, collis_mat, unk4, veget) = self.unpack("<II4sI4s", data)
        (name_size,) = self.unpack("<I", data[20:])
        (name,) = self.unpack("<" + str(name_size) + "s", data[24:])
        name = str(name, 'ascii').strip(chr(0))

        material = BESPteroMat(name)
        return material

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
            for bes_roots in bes.objects:
                # Create materials
                materials = []
                for PteroMat in bes_roots.materials:
                    materials.append(bpy.data.materials.new(PteroMat.name))

                # Create objects
                for bes_obj in bes_roots.children:
                    self.add_object(bes_obj, materials, None)

        return {'FINISHED'}

    def add_object(self, bes_obj, materials, parent):
        # Create new object
        bpy_obj = bpy.data.objects.new(bes_obj.name, None)
        bpy_obj.parent = parent

        # Since Blender does not allow multiple meshes for single object (while BES does),
        # we have to create seperate object for every mesh.
        for mesh_id in range(len(bes_obj.meshes)):
            bes_mesh = bes_obj.meshes[mesh_id]

            # In BES the meshes do not have names, so we create one from object name and mesh ID
            mesh_name = "{}.{:08X}".format(bes_obj.name, mesh_id)

            # Create new mesh
            bpy_mesh = bpy.data.meshes.new(mesh_name)

            # Update mesh data
            bpy_mesh.from_pydata(bes_mesh.vertices, [], bes_mesh.faces)
            bpy_mesh.update(calc_edges = True)

            # Create new object from mesh and add it into scene
            mesh_obj = bpy.data.objects.new(mesh_name, bpy_mesh)
            mesh_obj.location = bes_obj.position
            mesh_obj.parent = bpy_obj
            if bes_mesh.material != BESMaterial.NoneMaterial:
                mesh_obj.data.materials.append(materials[bes_mesh.material])
            bpy.context.scene.objects.link(mesh_obj)

        # Add children
        for bes_child in bes_obj.children:
            self.add_object(bes_child, materials, bpy_obj)

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

