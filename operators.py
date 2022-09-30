from email.policy import default
from unicodedata import name
import bpy


def skw_transfer_shapekeys(self, context):
    props = self.properties
    active = context.active_object
    selected = context.selected_objects

    # Validation
    if active is None or len(selected) <= 1:
        self.report({'ERROR'}, 'Invalid objects selection')
        return
    if active.type != 'MESH':
        self.report({'ERROR'}, f'Valid source (active) object type is "MESH". "{active.name}" type is "{active.type}"')
        return
    for obj in selected:
        if obj.type != 'MESH':
            self.report({'ERROR'}, f'Valid target object type is "MESH". "{obj.name}" type is "{obj.type}"')
            return
    if active.data.shape_keys is None:
        self.report({'ERROR'}, f'Source (active) object "{obj.name}" does not have shape keys.')
        return

    active_obj_show_only_shape_key = active.show_only_shape_key
    active_obj_active_shape_key_index = active.active_shape_key_index
    active.active_shape_key_index = 0
    active.show_only_shape_key = True
    
    num_sk = len(active.data.shape_keys.key_blocks)
    for target_obj in selected:
        if target_obj is active:
            continue

        target_obj_show_only_shape_key = target_obj.show_only_shape_key
        target_obj_active_shape_key_index = target_obj.active_shape_key_index
        target_obj.active_shape_key_index = 0
        target_obj.show_only_shape_key = True

        deformer = target_obj.modifiers.new(name='surface defrom', type='SURFACE_DEFORM')
        deformer.target = active
        deformer.falloff = props.falloff
        deformer.strength = props.strength
        bpy.ops.object.modifier_move_to_index(
            {"object" : target_obj},
            modifier=deformer.name, index=0
        )
        bpy.ops.object.surfacedeform_bind(
            {"object" : target_obj},
            modifier=deformer.name
        )
        
        for i in range(1, num_sk):
            active.active_shape_key_index = i
            sk = active.active_shape_key
            deformer.name = sk.name
            if props.replace_shapekeys:
                target_sks = target_obj.data.shape_keys
                if target_sks is not None and sk.name in target_sks.key_blocks.keys():
                    sk_index = target_sks.key_blocks.keys().index(sk.name)
                    target_obj.active_shape_key_index = sk_index
                    bpy.ops.object.shape_key_remove({"object" : target_obj})

            bpy.ops.object.modifier_apply_as_shapekey(
                {"object" : target_obj},
                keep_modifier=True,
                modifier=deformer.name, report=False
            )
        active.active_shape_key_index = 0

        target_obj.active_shape_key_index = target_obj_active_shape_key_index
        target_obj.show_only_shape_key = target_obj_show_only_shape_key
        target_obj.modifiers.remove(deformer)

    active.active_shape_key_index = active_obj_active_shape_key_index
    active.show_only_shape_key = active_obj_show_only_shape_key


class SKW_OT_transfer_shape_keys(bpy.types.Operator):
    bl_idname = "shape_key_wrap.transfer"
    bl_label = "Transfer from Active"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'REGISTER', 'UNDO'}

    replace_shapekeys: bpy.props.BoolProperty(
        name='!Replace Shapekeys',
        description='If it is ON, and target mesh have shape key with the same names as source'
            ' mesh they will be replaced. Be carefull with the checkbox because the key shape data '
            'may be lost irrecoverably.',
            default=False
        )
    falloff: bpy.props.FloatProperty(
        name='Interpolation Falloff',
        description='Surface Deform modifier property',
        default=4, min=2, max=14)
    strength: bpy.props.FloatProperty(
        name='Strength',
        description='Surface Deform modifier property',
        default=1, min=-100, max=100
        )

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        skw_transfer_shapekeys(self, context)
        return {'FINISHED'}


CLASSES = [SKW_OT_transfer_shape_keys]


def register():
    for c in CLASSES:
        bpy.utils.register_class(c)  


def unregister():
    for c in CLASSES:
        bpy.utils.unregister_class(c)


if __name__ == '__main__':
    register()
