import bpy
from .skw_operators import (
    SKW_OT_transfer_shape_keys,
    SKW_OT_refresh_shape_keys,
    skw_poll
)


def dropdown(
        layout: bpy.types.UILayout,
        config,
        attribute: str,
        text: str, icon: str = None,
        icon_value: str = None
) -> bool:
    row = layout.row(align=True)
    if row.prop(
            config,
            attribute,
            icon='TRIA_DOWN' if getattr(config, attribute) else 'TRIA_RIGHT',
            text=text,
            emboss=False
        ):
        setattr(config, attribute, not getattr(config, attribute))
    if icon:
        row.label(icon=icon, text="")
    elif icon_value:
        row.label(icon_value=icon_value, text="")

    return getattr(config, attribute)


class SKT_UL_items(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.label(text=item.name, icon='SHAPEKEY_DATA')
        row.prop(item, 'checked', text='')


def draw_poll(context: bpy.types.Context, layout: bpy.types.UILayout) -> None:
    result, reason = skw_poll(context)
    if result:
        col = layout.column(align=True)
        lines = reason.split('\n')
        for line in lines:
            col.label(text=line)
    else:
        layout.label(text=reason)


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

        active = context.active_object
        
        if not active or active.type != 'MESH':
            layout(text='Selection is invalid')
            return
        
        mesh = active.data
        skw = mesh.skw_prop
        # row = layout.row(align=True)        
        

        if dropdown(layout, skw, 'show_transfer_block', text='Transfer Shape Keys', icon='MOD_DATA_TRANSFER'):
            box = layout.box()
            draw_poll(context, box)
            col = box.column()
            if skw.bind_noise:
                sub_box = col.box()
                
                row = sub_box.row()
                row.prop(skw, 'bind_noise', text='Bind Noise')
                row.label(icon='LINKED')
                
                sub_box.prop(skw, 'min_noise', text='Min Noise')
                sub_box.prop(skw, 'max_noise', text='Max Noise')
            else:
                row = col.row()
                row.prop(skw, 'bind_noise', text='Bind Noise')
                row.label(icon='LINKED')
            
            row = col.row()
            
            row.prop(skw, 'bind_values', text='Add Drivers')
            row.label(icon='DRIVER')
            
            col.prop(skw, 'overwrite_shapekeys', text='!Overwrite Shape Keys')
            
            if skw.delete_empty:
                sub_box = col.box()
                row = sub_box.row()
                row.prop(skw, 'delete_empty', text='Delete Empty')
                row.label(icon='FILTER')
                sub_box.prop(skw, 'empty_threshold', text='Threshold')
            else:
                row = col.row()
                row.prop(skw, 'delete_empty', text='Delete Empty')
                row.label(icon='FILTER')
            
            if skw.transfer_by_list:
                sub_box = col.box()
                row = sub_box.row()
                row.prop(skw, 'transfer_by_list', text='Transfer By The List')
                row.label(icon='LINENUMBERS_ON')

                col = sub_box.column(align=True)
                col.enabled = skw.transfer_by_list
                col.template_list(
                    'SKT_UL_items', '',
                    skw, 'shape_keys_to_transfer',
                    skw, 'shape_key_index',
                    rows=5
                )
                col.operator(SKW_OT_refresh_shape_keys.bl_idname, text='Refresh').action = 'REFRESH'
                row = col.row(align=True)
                row.operator(SKW_OT_refresh_shape_keys.bl_idname, text='Check All').action = 'CHECK_ALL'
                row.operator(SKW_OT_refresh_shape_keys.bl_idname, text='Uncheck All').action = 'UNCHECK_ALL'
            else:
                row = col.row()
                row.prop(skw, 'transfer_by_list', text='Transfer By The List')
                row.label(icon='LINENUMBERS_ON')

            row = box.row()
            row.scale_y = 2.0
            props = row.operator(SKW_OT_transfer_shape_keys.bl_idname, text='Transfer Shape Keys', icon='ARROW_LEFTRIGHT')

        # col.operator(SKW_OT_bind_shape_key_values.bl_idname, text='Bind Values', icon='DRIVER')


classes = [SKT_PT_object_mode, SKT_UL_items]


def register():
    for c in classes:
        bpy.utils.register_class(c)  


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == '__main__':
    register()
