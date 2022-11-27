import bpy


class SKW_ExceptionItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default='')


def register():
    bpy.utils.register_class(SKW_ExceptionItem)
    bpy.types.Mesh.skw_exceptions = bpy.props.CollectionProperty(
        name='SKW Exceptions',
        type=SKW_ExceptionItem
    )


def unregister():
    bpy.utils.unregister_class(SKW_ExceptionItem)
    del bpy.types.Mesh.skw_exceptions
