import bpy
from . import panel
from . import operators


bl_info = {
    'name' : 'ShapeKeyWrap',
    'author' : 'Mykyta Petrenko (Squeezy Weasel)',
    'description' : 'Blender addon for transfering shapekeys from on mesh to another one using surface deform modifier.',
    'blender' : (3, 3, 0),
    'version' : (0, 1, 0),
    'location' : 'View3D -> Object Mode -> N-Panel -> Tools -> Shape Key Wrap',
    'warning' : '',
    'category' : 'Mesh'
}

MODULES = [panel, operators]


def register():
    for module in MODULES:
        module.register()


def unregister():
    for module in MODULES:
        module.unregister()


if __name__ == "__main__":
    register()
