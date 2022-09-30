import bpy
import bmesh


def transfer_shapekeys(self, context):
    active = context.active_object
    selected = context.selected_objects
    show_only_shape_key = active.show_only_shape_key
    active_shape_key_index = active.active_shape_key_index
    active.active_shape_key_index = 0
    active.show_only_shape_key = True

    
    num_sk = len(active.data.shape_keys.key_blocks)
    for obj in selected:
        if obj is active:
            continue

        deformer = obj.modifiers.new(name='JUST_FOR_TEST', type='SURFACE_DEFORM')
        deformer.target = active
        bpy.ops.object.modifier_move_to_index(
            {"object" : obj},
            modifier=deformer.name, index=0
        )
        bpy.ops.object.surfacedeform_bind(
            {"object" : obj},
            modifier=deformer.name
        )
        
        for i in range(1, num_sk):
            active.active_shape_key_index = i
            sk = active.active_shape_key
            deformer.name = sk.name
            bpy.ops.object.modifier_apply_as_shapekey(
                {"object" : obj},
                keep_modifier=True,
                modifier=deformer.name, report=False
            )
            print(sk.name)
        active.active_shape_key_index = 0
        obj.modifiers.remove(deformer)

    active.active_shape_key_index = active_shape_key_index
    active.show_only_shape_key = show_only_shape_key


class FSEAL_OT_transfer_shapekeys(bpy.types.Operator):
    bl_idname = "shapekey_transfer.transfer"
    bl_label = "Transfer from Active"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'REGISTER', 'UNDO'}

    falloff: bpy.props.FloatProperty(name='Interpolation Falloff', default=4, min=2, max=14)
    strength: bpy.props.FloatProperty(name='Strength', default=1, min=-100, max=100)

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        transfer_shapekeys(self, context)
        return {'FINISHED'}
