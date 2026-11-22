import bpy
from typing import List


def smooth_shape_keys(
        context: bpy.types.Context,
        obj: bpy.types.Object,
        factor: float = 0.5,
        iterations: int = 5,
        scale: float = 1.0,
        smooth_type: str = 'SIMPLE',
        overwrite_shape_keys: bool = False,
        shape_keys: List[str] | None = None
) -> None:
    """Smooth non-reference shape keys with a temporary Corrective Smooth modifier."""
    obj_show_only_shape_key = obj.show_only_shape_key
    obj_active_shape_key_index = obj.active_shape_key_index
    mod = obj.modifiers.new(name='Corrective Smooth', type='CORRECTIVE_SMOOTH')
    try:
        obj.show_only_shape_key = True
        mod.factor = factor
        mod.iterations = iterations
        mod.smooth_type = smooth_type
        mod.scale = scale

        with context.temp_override(object=obj):
            bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=0)

        key_blocks = obj.data.shape_keys.key_blocks
        for sk in key_blocks[1:]:
            if shape_keys is not None and sk.name not in shape_keys:
                continue
            obj.active_shape_key_index = key_blocks.find(sk.name)
            previous_count = len(key_blocks)
            with context.temp_override(object=obj):
                status = bpy.ops.object.modifier_apply_as_shapekey(
                    keep_modifier=True,
                    modifier=mod.name,
                    report=False
                )
            if 'FINISHED' not in status or len(key_blocks) != previous_count + 1:
                raise RuntimeError(f'Unable to apply corrective smooth to shape key "{sk.name}"')

            new_sk = key_blocks[-1]
            if overwrite_shape_keys:
                sk.data.foreach_set("co", [value for point in new_sk.data for value in point.co[:]])
                obj.shape_key_remove(new_sk)
            else:
                new_sk.name = f'CS_{sk.name}'
    finally:
        obj.active_shape_key_index = obj_active_shape_key_index
        obj.show_only_shape_key = obj_show_only_shape_key
        obj.modifiers.remove(mod)
