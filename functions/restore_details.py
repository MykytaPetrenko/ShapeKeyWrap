import bpy
from typing import List


def restore_details(
        context: bpy.types.Context,
        obj: bpy.types.Object,
        vertex_group: str,
        factor: float = 1.0,
        iterations: int = 20,
        scale: float = 1.0,
        smooth_type: str = 'SIMPLE',
        overwrite_shape_keys: bool = False,
        shape_keys: List[str] | None = None
) -> None:
    obj_show_only_shape_key = obj.show_only_shape_key
    obj_active_shape_key_index = obj.active_shape_key_index

    obj.active_shape_key_index = 0
    obj.show_only_shape_key = True

    mod: bpy.types.CorrectiveSmoothModifier = obj.modifiers.new(name='Corrective Smooth', type='CORRECTIVE_SMOOTH')
    mod.factor = factor
    mod.iterations = iterations
    mod.smooth_type = smooth_type
    mod.scale = scale
    mod.vertex_group = vertex_group

    with context.temp_override(object=obj):
        bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=0)

    sk_names = [sk.name for sk in obj.data.shape_keys.key_blocks[1:]]
    for sk_name in sk_names:
        
        sk = obj.data.shape_keys.key_blocks.get(sk_name)
        if shape_keys is not None and sk.name not in shape_keys:
            continue
        
        # Set SK index
        obj.active_shape_key_index = obj.data.shape_keys.key_blocks.keys().index(sk_name)
        
        with context.temp_override(object=obj):
            bpy.ops.object.modifier_apply_as_shapekey(
                keep_modifier=True,
                modifier=mod.name,
                report=False
            )
        new_sk = obj.data.shape_keys.key_blocks[-1]
        
        if new_sk.name in sk_names:
            raise Exception('Unable to apply corrective smooth modifier')
    
        if overwrite_shape_keys:
            
            # Use foreach_set to batch update the original shape key data
            sk.data.foreach_set("co", [value for v in new_sk.data for value in v.co[:]])
            
            # Remove the new shape key
            with context.temp_override(object=obj):
                sk_index = len(obj.data.shape_keys.key_blocks) - 1
                obj.active_shape_key_index = sk_index
                bpy.ops.object.shape_key_remove()

            # Note. We do not remove old shape key renaming the new one to keep the original order
                
        else:
            new_sk.name = f'RD_{sk_name}'

    obj.active_shape_key_index = obj_active_shape_key_index
    obj.show_only_shape_key = obj_show_only_shape_key
    obj.modifiers.remove(mod)
