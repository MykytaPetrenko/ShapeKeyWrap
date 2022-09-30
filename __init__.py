import bpy
from .panel import VIEW3D_PT_shapekeys_transfer
from .operator import FSEAL_OT_transfer_shapekeys


bl_info = {
    "name" : "Cloth Shape Keys",
    "author" : "Mykyta Petrenko (FSeal)",
    "description" : "Simple addon that copies the position of the active vertex to the selected with invertion of the chosen axis.",
    "blender" : (2, 80, 0),
    "version" : (0, 1, 0),
    "location" : "View3D -> Mesh Edit Mode -> N-Panel -> FSeaL -> Vertex Symmetrizer",
    "warning" : "",
    "category" : "Mesh"
}

CLASSES = [
    VIEW3D_PT_shapekeys_transfer,
    FSEAL_OT_transfer_shapekeys
]

def add_object_button(self, context):
    self.layout.operator(
        FSEAL_OT_transfer_shapekeys.bl_idname,
        text="Transfer From Active",
        icon='PLUGIN')

def register():
    for c in CLASSES:
        bpy.utils.register_class(c)  


def unregister():
    for c in CLASSES:
        bpy.utils.unregister_class(c)


if __name__ == "__main__":
    register()
