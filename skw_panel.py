import bpy
from .skw_operators import SKW_OT_transfer_shape_keys


class SKW_PT_object_mode(bpy.types.Panel):
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
        
        selected = context.selected_objects
        active = context.active_object
        transfer_targets = list()
        for obj in selected:
            if obj is active:
                continue
            transfer_targets.append(obj)

        row = layout.row()
        row.operator(SKW_OT_transfer_shape_keys.bl_idname, text='Transfer from Active', icon='ARROW_LEFTRIGHT')
        
        if active:
            layout.row().label(text=f'From: {active.name}')
        col = layout.column(align=True)
        if transfer_targets:
            col.label(text='To:')
        for obj in transfer_targets:
            col.label(text=obj.name)

def register():
    bpy.utils.register_class(SKW_PT_object_mode)  


def unregister():
    bpy.utils.unregister_class(SKW_PT_object_mode)


if __name__ == '__main__':
    register()
