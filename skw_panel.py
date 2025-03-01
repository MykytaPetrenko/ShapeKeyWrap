import bpy
from .skw_operators import (
    SKW_OT_transfer_shape_keys,
    SKW_OT_refresh_shape_keys,
    SKW_OT_bind_shape_key_values,
    SKW_OT_remove_drivers,
    SKW_OT_remove_empty_shape_keys,
    SKW_OT_smooth_shape_keys,
    skw_poll
)
from .skw_validate_mesh import (
    SKW_OT_validate_edges,
    SKW_OT_validate_faces
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


class SKW_UL_items(bpy.types.UIList):
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
        if dropdown(box, skw, 'show_transfer_panel', 'Transfer Shape Keys', icon='MOD_DATA_TRANSFER'):
            col = box.column()
            col.label(text='Surface Deform Parameters')            
            col.prop(skw, 'surface_deform_method', text='Method')
            
            if skw.surface_deform_method != 'SQUEEZY_PIXELS':
                if skw.use_bind_noise:
                    noise_box = col.box()
                    
                    noise_box.prop(skw, 'use_bind_noise', text='Use Bind Noise')
                    sub_col = noise_box.column(align=True)
                    sub_col.prop(skw, 'min_noise', text='Min Noise')
                    sub_col.prop(skw, 'max_noise', text='Max Noise')

                else:
                    col.prop(skw, 'use_bind_noise', text='Use Bind Noise')

                col.prop(skw, 'sd_falloff', text='Falloff')
                col.prop(skw, 'sd_strength', text='Strength')
                    
            col.separator()
            col.label(text='Additional Parameters')    
            col.prop(skw, 'bind_drivers', text='Add Drivers')
            
            col.prop(skw, 'overwrite_shape_keys', text='!Overwrite Shape Keys')
            
            if skw.remove_empty_shape_keys:
                
                sub_box = col.box()
                sub_box.prop(skw, 'remove_empty_shape_keys', text='Delete Empty')
                sub_box.prop(skw, 'empty_threshold', text='Threshold')

            else:
                col.prop(skw, 'remove_empty_shape_keys', text='Delete Empty')
            
            if skw.smooth_shape_keys:
                sub_box = col.box()
                sub_box.prop(skw, 'smooth_shape_keys', text='Corrective Smooth')

                sub_col = sub_box.column(align=True)
                sub_col.prop(skw, 'cs_factor', text='Factor')
                sub_col.prop(skw, 'cs_iterations', text='Iterations')
                sub_col.prop(skw, 'cs_scale', text='Scale')

                sub_box.prop(skw, 'cs_smooth_type', text='Method')
            else:
                col.prop(skw, 'smooth_shape_keys', text='Smooth')

            split = box.split(factor=0.75, align=True)
            split.scale_y = 2.0
            
            split.operator(SKW_OT_transfer_shape_keys.bl_idname, text='Transfer Shape Keys', icon='ARROW_LEFTRIGHT')
            split.prop(skw, 'use_shape_key_list', text='Use List', toggle=True)
        
        box = layout.box()
        if dropdown(box, skw, 'show_utilities_panel', 'Utils', icon='TOOL_SETTINGS'):
            sub_box = box.box()
            sub_box.label(text='Add Drivers')
            sub_box.operator(SKW_OT_bind_shape_key_values.bl_idname, text='Add Drivers')
            if len(context.selected_objects) > 1:
                row = box.row(align=False)
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
            split.prop(skw, 'use_shape_key_list', text='Use List', toggle=True)
            
            
            # 'Delete empty' block
            sub_box = box.box()
            sub_box.label(text='Delete Empty Shape Keys:')
            sub_box.prop(skw, 'empty_threshold', text='Threshold')
            split = sub_box.split(factor=0.75, align=True)
            split.operator(SKW_OT_remove_empty_shape_keys.bl_idname, text='Delete')
            split.prop(skw, 'use_shape_key_list', text='Use List', toggle=True)
            
            # 'Corrective smooth' block
            sub_box = box.box()
            sub_box.label(text='Corrective Smooth:', icon='MOD_SMOOTH')
            
            sub_box.prop(skw, 'cs_smooth_type', text='Method')
            col = sub_box.column(align=True)
            col.separator()
            col.prop(skw, 'cs_factor', text='Factor')
            col.prop(skw, 'cs_iterations', text='Iterations')
            col.prop(skw, 'cs_scale', text='Scale')
            col.prop(skw, 'overwrite_shape_keys', text='!Overwrite Shape Keys')
            
            split = sub_box.split(factor=0.75, align=True)
            split.operator(SKW_OT_smooth_shape_keys.bl_idname, text='Smooth Shape Keys')
            split.prop(skw, 'use_shape_key_list', text='Use List', toggle=True)

            # Validate block
            sub_box = box.box()
            sub_box.label(text='Validate:', icon='MOD_SMOOTH')
            sub_col = sub_box.column(align=True)
            sub_col.operator(SKW_OT_validate_edges.bl_idname, text='Check Edges (3+ linked faces)')
            sub_col.operator(SKW_OT_validate_faces.bl_idname, text='Check Faces (Concave)')

        
        box = layout.box()
        if dropdown(box, skw, 'show_shape_key_list_panel', 'Shape Key List', icon='SHAPEKEY_DATA'):
            col = box.column(align=True)
            col.label(text='List of Shape Keys:')
            col.enabled = skw.use_shape_key_list
            col.template_list(
                'SKW_UL_items', '',
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
            


classes = [SKW_PT_object_mode, SKW_UL_items]


def register():
    for c in classes:
        bpy.utils.register_class(c)  


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)


if __name__ == '__main__':
    register()
