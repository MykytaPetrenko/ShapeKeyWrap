import bpy
from . import skw_panel
from . import skw_operators
from . import skw_props
from . import skw_validate_mesh


bl_info = {
    'name' : 'ShapeKeyWrap',
    'author' : 'Mykyta Petrenko (Squeezy Pixels)',
    'description' : 'Blender addon for transfering shapekeys from on mesh to another one using surface deform modifier.',
    'blender' : (3, 6, 0),
    'version' : (0, 5, 1),
    'location' : 'View3D > Object Mode > N-Panel > Tools > Shape Key Wrap',
    'warning' : '',
    'doc_url': 'https://github.com/MykytaPetrenko/ShapeKeyWrap',
    'category': 'Mesh'
}

MODULES = [skw_props, skw_panel, skw_operators, skw_validate_mesh]


def register():
    for module in MODULES:
        module.register()


def unregister():
    for module in MODULES:
        module.unregister()


if __name__ == '__main__':
    register()
