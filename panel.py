import bpy
from .operator import FSEAL_OT_transfer_shapekeys


class VIEW3D_PT_shapekeys_transfer(bpy.types.Panel):
    """
    Addon main menu (N-Panel)
    """
    bl_label = "SKHelper"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'
    bl_context = 'objectmode'

    def draw(self, context):                
        layout = self.layout
        row = layout.row()
        props = row.operator(FSEAL_OT_transfer_shapekeys.bl_idname, text='Transfer Shape Keys')

