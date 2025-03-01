import bpy
from typing import List


def delete_empty_shape_keys(
        context: bpy.types.Context,
        obj: bpy.types.Object,
        empty_threshold: float,
        shape_keys: List[str] | None = None
) -> int:
    nullshapekeysdeleted = 0
    shape_keys_to_remove = []

    for sk in obj.data.shape_keys.key_blocks[1:]:
        if shape_keys is not None and sk.name not in shape_keys:
            continue

        is_empty = True
        for v in obj.data.vertices:
            delta = sk.data[v.index].co - v.co

            # If any displacement is above the threshold, mark the shape key as not empty
            if delta.length > empty_threshold:
                is_empty = False
                break

        # If the shape key is empty (below the threshold), mark it for deletion
        if is_empty:
            shape_keys_to_remove.append(sk)
        
    with context.temp_override(object=obj):
        # Check if the skp_shape_key_remove operator is available
        operator_to_use = bpy.ops.object.shape_key_remove
        if "skp_shape_key_remove" in dir(bpy.ops.object):
            operator_to_use = bpy.ops.object.skp_shape_key_remove

        # Delete the shape keys marked for removal (outside the loop to avoid modifying the collection during iteration)
        for key in shape_keys_to_remove:
            iIndex = obj.data.shape_keys.key_blocks.keys().index(key.name)
            obj.active_shape_key_index = iIndex

            # Use the selected operator to delete the shape key
            operator_to_use('EXEC_DEFAULT')
            nullshapekeysdeleted += 1
    
    return nullshapekeysdeleted
