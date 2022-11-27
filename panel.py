import bpy
from .operators import SKW_OT_transfer_shape_keys, skw_poll_transfer_shapekeys


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

        result, reason = skw_poll_transfer_shapekeys(context)
        if result:
            col = layout.column(align=True)
            lines = reason.split('\n')
            for line in lines:
                col.label(text=line)
        else:
            layout.label(text=reason)
        row = layout.row()
        row.operator(SKW_OT_transfer_shape_keys.bl_idname, text='Transfer from Active', icon='ARROW_LEFTRIGHT')


def register():
    bpy.utils.register_class(SKT_PT_object_mode)  


def unregister():
    bpy.utils.unregister_class(SKT_PT_object_mode)


if __name__ == '__main__':
    register()
