import bpy
from .skw_operators import (
    SKW_OT_transfer_shape_keys,
    SKW_OT_refresh_shape_keys,
    SKW_OT_bind_shape_key_values,
    skw_poll_transfer_shapekeys
)


class SKT_UL_items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name, icon='SHAPEKEY_DATA')
        row.prop(item, 'checked', text='')


class SKT_PT_object_mode(bpy.types.Panel):
    """
    Addon main menu (N-Panel)
    """
    bl_label = 'Shape Key Wrap UwU'
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

        active = context.active_object
        
        if active and active.type == 'MESH':
            mesh = active.data
            skw = mesh.skw_prop
            layout.prop(skw, 'bind_noise', text='Bind Noise')
            if skw.bind_noise:
                layout.prop(skw, 'min_noise', text='Min Noise')
                layout.prop(skw, 'max_noise', text='Max Noise')
            layout.prop(skw, 'delete_empty', text='Delete Empty')
            if skw.delete_empty:
                layout.prop(skw, 'empty_threshold', text='Threshold')
            layout.prop(skw, 'transfer_by_list', text='Transfur By The Lwist', toggle=True)
            col = layout.column(align=True)
            col.enabled = skw.transfer_by_list
            col.template_list(
                'SKT_UL_items', '',
                skw, 'shape_keys_to_transfer',
                skw, 'shape_key_index',
                rows=5
            )
            col.operator(SKW_OT_refresh_shape_keys.bl_idname, text='Refwesh').action = 'REFRESH'
            row = col.row(align=True)
            row.operator(SKW_OT_refresh_shape_keys.bl_idname, text='Sewect All').action = 'CHECK_ALL'
            row.operator(SKW_OT_refresh_shape_keys.bl_idname, text='Unsewect All').action = 'UNCHECK_ALL'

        box = layout.box()
        col = box.column(align=True)
        col.operator(SKW_OT_transfer_shape_keys.bl_idname, text='Transfur Shape Keys', icon='ARROW_LEFTRIGHT')
        col.operator(SKW_OT_bind_shape_key_values.bl_idname, text='Bind Valuwues', icon='DRIVER')


classes = [SKT_PT_object_mode, SKT_UL_items]


def register():
    for c in classes:
        bpy.utils.register_class(c)  


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == '__main__':
    register()
