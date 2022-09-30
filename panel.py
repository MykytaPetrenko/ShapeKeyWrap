import bpy
from .operators import SKW_OT_transfer_shape_keys


class SKT_PT_object_mode(bpy.types.Panel):
    """
    Addon main menu (N-Panel)
    """
    bl_label = 'Shape Key Wrap'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'
    bl_context = 'objectmode'

    def draw(self, context):                
        layout = self.layout
        row = layout.row()
        props = row.operator(SKW_OT_transfer_shape_keys.bl_idname, text='Transfer from Active', icon='ARROW_LEFTRIGHT')


def register():
    bpy.utils.register_class(SKT_PT_object_mode)  


def unregister():
    bpy.utils.unregister_class(SKT_PT_object_mode)


if __name__ == '__main__':
    register()
