import bpy
from typing import List
import mathutils
import random


class IsNotBoundException(Exception):
    pass


def transfer_shape_keys(
        context: bpy.types.Context,
        from_obj: bpy.types.Object,
        to_objs: List[bpy.types.Object],
        falloff: float,
        strength: float,
        replace_existing_shape_keys: bool = False,
        transfer_list: List[str] | None = None,
        bind_noise: tuple | None = None
) -> None:
    from_obj.show_only_shape_key = False
    for sk in from_obj.data.shape_keys.key_blocks:
        sk.value = 0.0

    noise_key_name = None
    if bind_noise is not None:
        min_noise, max_noise = bind_noise
        # Add a new shape key
        noise_key = from_obj.shape_key_add(name="DELTA_NOISE", from_mix=False)
        noise_key_name = noise_key.name
        from_obj.data.update()
        # Get the vertex normals from the current shape
        normals = [vertex.normal for vertex in from_obj.data.vertices]
        # Apply random offset to each vertex in the shape key
        for i, vertex in enumerate(noise_key.data):
            offset = normals[i] * random.uniform(min_noise, max_noise)
            vertex.co +=  mathutils.Vector(offset)
        noise_key.value = 1.0   
    
    for tgt_obj in to_objs:
        if tgt_obj is from_obj:
            continue
        tgt_obj_show_only_shape_key = tgt_obj.show_only_shape_key
        tgt_obj_active_shape_key_index = tgt_obj.active_shape_key_index
        tgt_obj.active_shape_key_index = 0
        tgt_obj.show_only_shape_key = True

        deformer = tgt_obj.modifiers.new(name='surface defrom', type='SURFACE_DEFORM')
        deformer.target = from_obj
        deformer.falloff = falloff
        deformer.strength = strength

        with context.temp_override(object=tgt_obj):
            bpy.ops.object.modifier_move_to_index(modifier=deformer.name, index=0)
            bpy.ops.object.surfacedeform_bind(modifier=deformer.name)

        if not deformer.is_bound:
            # Remove Noise Shape Key
            if noise_key_name:
                index = from_obj.data.shape_keys.key_blocks.find(noise_key_name)
                if index > 0:
                    from_obj.active_shape_key_index = index
                    bpy.ops.object.shape_key_remove()
            raise IsNotBoundException()
        
        for sk in from_obj.data.shape_keys.key_blocks[1:]:
            # Skip temp noise shape key
            if sk.name == noise_key_name:
                continue
            if transfer_list is not None and sk.name not in transfer_list:
                continue
            
            sk.value = 1.0
            deformer.name = sk.name
            if replace_existing_shape_keys:
                target_sks = tgt_obj.data.shape_keys
                if target_sks is not None and sk.name in target_sks.key_blocks.keys():
                    sk_index = target_sks.key_blocks.keys().index(sk.name)
                    tgt_obj.active_shape_key_index = sk_index
                    with context.temp_override(object=tgt_obj):
                        bpy.ops.object.shape_key_remove()

            with context.temp_override(object=tgt_obj):
                bpy.ops.object.modifier_apply_as_shapekey(
                    keep_modifier=True,
                    modifier=deformer.name,
                    report=False
                )
            sk.value = 0.0

        tgt_obj.active_shape_key_index = tgt_obj_active_shape_key_index
        tgt_obj.show_only_shape_key = tgt_obj_show_only_shape_key
        tgt_obj.modifiers.remove(deformer)

    # Remove Noise Shape Key
    if noise_key_name:
        index = from_obj.data.shape_keys.key_blocks.find(noise_key_name)
        if index > 0:
            from_obj.active_shape_key_index = index
            bpy.ops.object.shape_key_remove() 
   