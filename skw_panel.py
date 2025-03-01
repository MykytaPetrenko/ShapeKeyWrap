import bpy
from .skw_operators import (
    SKW_OT_transfer_shape_keys,
    SKW_OT_refresh_shape_keys,
    SKW_OT_bind_shape_key_values,
    SKW_OT_remove_drivers,
    SKW_OT_delete_empty_shape_keys,
    SKW_OT_smooth_shape_keys,
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
            layout.label(text='Selection is invalid')
            return
        
        mesh = active.data
        skw_sk_list = mesh.skw_sk_list
        skw = context.scene.skw_prop
        # row = layout.row(align=True)        
        

        draw_poll(context, layout)
        box = layout.box()
        if dropdown(box, skw, 'show_transfer_block', 'Transfer Shape Keys', icon='MOD_DATA_TRANSFER'):
            col = box.column()
            if skw.bind_noise:
                sub_col = col.column(align=True)
                sub_col.separator()
                sub_col.prop(skw, 'bind_noise', text='Bind Noise')
                
                sub_col.prop(skw, 'min_noise', text='Min Noise')
                sub_col.prop(skw, 'max_noise', text='Max Noise')
                sub_col.separator()
            else:
                col.prop(skw, 'bind_noise', text='Bind Noise')
                    
            col.prop(skw, 'bind_values', text='Add Drivers')
            
            col.prop(skw, 'overwrite_shapekeys', text='!Overwrite Shape Keys')
            
            if skw.delete_empty:
                sub_col = col.column(align=True)
                sub_col.separator()
                sub_col.prop(skw, 'delete_empty', text='Delete Empty')
                sub_col.prop(skw, 'empty_threshold', text='Threshold')
                sub_col.separator()
            else:
                col.prop(skw, 'delete_empty', text='Delete Empty')
            
            if skw.smooth_shape_keys:
                sub_col = col.column(align=True)
                sub_col.separator()
                sub_col.prop(skw, 'smooth_shape_keys', text='Smooth')
                sub_col.prop(skw, 'cs_factor', text='Factor')
                sub_col.prop(skw, 'cs_iterations', text='Iterations')
                sub_col.prop(skw, 'cs_scale', text='Scale')
                sub_col.prop(skw, 'cs_smooth_type', text='Method')
                sub_col.separator()
            else:
                col.prop(skw, 'smooth_shape_keys', text='Smooth')

            split = box.split(factor=0.75, align=True)
            split.scale_y = 2.0
            
            split.operator(SKW_OT_transfer_shape_keys.bl_idname, text='Transfer Shape Keys', icon='ARROW_LEFTRIGHT')
            split.prop(skw, 'transfer_by_list', text='Use List', toggle=True)
        
        box = layout.box()
        if dropdown(box, skw, 'show_utils_block', 'Utils', icon='TOOL_SETTINGS'):
            sub_box = box.box()
            sub_box.label(text='Add Drivers')
            sub_box.operator(SKW_OT_bind_shape_key_values.bl_idname, text='Add Drivers')
            if len(context.selected_objects) > 1:
                row = layout.row(align=False)
                col=row.column(align=True)
                col.scale_y = 2.0
                col.label(icon='INFO')
                col = row.column(align=True)
                col.label(text='The operators below process')
                col.label(text='a single (active) object only!')
            
            
            sub_box = box.box()
            sub_box.label(text='Delete Drivers:')
            split = sub_box.split(factor=0.75, align=True)
            split.operator(SKW_OT_remove_drivers.bl_idname, text='Delete')
            split.prop(skw, 'transfer_by_list', text='Use List', toggle=True)
            
            
            # 'Delete empty' block
            sub_box = box.box()
            sub_box.label(text='Delete Empty Shape Keys:')
            sub_box.prop(skw, 'empty_threshold', text='Threshold')
            split = sub_box.split(factor=0.75, align=True)
            split.operator(SKW_OT_delete_empty_shape_keys.bl_idname, text='Delete')
            split.prop(skw, 'transfer_by_list', text='Use List', toggle=True)
            
            # 'Corrective smooth' block
            sub_box = box.box()
            sub_box.label(text='Corrective Smooth:', icon='MOD_SMOOTH')
            
            sub_box.prop(skw, 'cs_smooth_type', text='Method')
            col = sub_box.column(align=True)
            col.separator()
            col.prop(skw, 'cs_factor', text='Factor')
            col.prop(skw, 'cs_iterations', text='Iterations')
            col.prop(skw, 'cs_scale', text='Scale')
            col.prop(skw, 'overwrite_shapekeys', text='!Overwrite Shape Keys')
            
            split = sub_box.split(factor=0.75, align=True)
            split.operator(SKW_OT_smooth_shape_keys.bl_idname, text='Smooth Shape Keys')
            split.prop(skw, 'transfer_by_list', text='Use List', toggle=True)

        
        box = layout.box()
        if dropdown(box, skw, 'show_shape_key_list', 'Shape Key List', icon='SHAPEKEY_DATA'):
            col = box.column(align=True)
            col.label(text='List of Shape Keys:')
            col.enabled = skw.transfer_by_list
            col.template_list(
                'SKT_UL_items', '',
                skw_sk_list, 'shape_keys_to_process',
                skw_sk_list, 'shape_key_index',
                rows=5
            )

            row = col.row(align=True)
            row.operator(SKW_OT_refresh_shape_keys.bl_idname, text='Refresh').action = 'REFRESH'
            row.operator(SKW_OT_refresh_shape_keys.bl_idname, text='', icon='ARROW_LEFTRIGHT').action = 'INVERT'
            row = col.row(align=True)
            row.operator(SKW_OT_refresh_shape_keys.bl_idname, text='Check All').action = 'CHECK_ALL'
            row.operator(SKW_OT_refresh_shape_keys.bl_idname, text='Uncheck All').action = 'UNCHECK_ALL'
            


classes = [SKT_PT_object_mode, SKT_UL_items]


def register():
    for c in classes:
        bpy.utils.register_class(c)  


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == '__main__':
    register()
