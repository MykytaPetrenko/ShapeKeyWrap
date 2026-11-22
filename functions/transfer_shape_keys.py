import bpy
from typing import Callable, List
import mathutils
import random
from .bind_drivers import shape_key_add_binding_driver
from .transfer_key_name import transfer_key_name


class IsNotBoundException(Exception):
    pass


def transfer_shape_keys(
        context: bpy.types.Context,
        from_obj: bpy.types.Object,
        to_objs: List[bpy.types.Object],
        falloff: float,
        strength: float,
        overwrite_shape_keys: bool = False,
        shape_keys: List[str] | None = None,
        bind_noise: tuple | None = None,
        create_drivers: bool = False,
        report: Callable[[set[str], str], None] | None = None
) -> dict[str, list[str]]:
    result = {obj.name: list() for obj in to_objs}
    source_keys = from_obj.data.shape_keys.key_blocks
    source_names = set(source_keys.keys())
    names_to_transfer = [
        sk.name for sk in source_keys[1:]
        if shape_keys is None or sk.name in shape_keys
    ]
    if not names_to_transfer:
        return result

    from_obj.show_only_shape_key = False
    for sk in source_keys:
        sk.value = 0.0

    noise_key = None
    try:
        if bind_noise is not None:
            min_noise, max_noise = bind_noise
            noise_key = from_obj.shape_key_add(name="DELTA_NOISE", from_mix=False)
            from_obj.data.update()
            normals = [vertex.normal for vertex in from_obj.data.vertices]
            for vertex, normal in zip(noise_key.data, normals):
                offset = normal * random.uniform(min_noise, max_noise)
                vertex.co += mathutils.Vector(offset)
            noise_key.value = 1.0

        for tgt_obj in to_objs:
            if tgt_obj is from_obj:
                continue
            show_only_shape_key = tgt_obj.show_only_shape_key
            active_index = tgt_obj.active_shape_key_index
            active_key = tgt_obj.active_shape_key
            active_name = active_key.name if active_key is not None else None
            deformer = tgt_obj.modifiers.new(name='Surface Deform', type='SURFACE_DEFORM')
            try:
                tgt_obj.active_shape_key_index = 0
                tgt_obj.show_only_shape_key = True
                deformer.target = from_obj
                deformer.falloff = falloff
                deformer.strength = strength

                with context.temp_override(object=tgt_obj):
                    bpy.ops.object.modifier_move_to_index(modifier=deformer.name, index=0)
                    bpy.ops.object.surfacedeform_bind(modifier=deformer.name)

                if not deformer.is_bound:
                    raise IsNotBoundException()

                for name in names_to_transfer:
                    sk = source_keys[name]
                    target_name = transfer_key_name(name, source_names, tgt_obj, report)
                    target_keys = tgt_obj.data.shape_keys
                    previous_count = len(target_keys.key_blocks) if target_keys is not None else 0
                    replaced_key = None
                    if overwrite_shape_keys and target_keys is not None:
                        replaced_key = target_keys.key_blocks.get(target_name)

                    tgt_obj.active_shape_key_index = 0
                    sk.value = 1.0
                    with context.temp_override(object=tgt_obj):
                        status = bpy.ops.object.modifier_apply_as_shapekey(
                            keep_modifier=True,
                            modifier=deformer.name,
                            report=False
                        )
                    sk.value = 0.0
                    target_keys = tgt_obj.data.shape_keys
                    expected_count = max(1, previous_count) + 1
                    if ('FINISHED' not in status or target_keys is None
                            or len(target_keys.key_blocks) != expected_count):
                        raise RuntimeError(f'Unable to transfer shape key "{name}" to "{tgt_obj.name}"')

                    new_sk = target_keys.key_blocks[-1]
                    if replaced_key is not None:
                        tgt_obj.shape_key_remove(replaced_key)
                    new_sk.name = target_name
                    if create_drivers:
                        shape_key_add_binding_driver(sk=new_sk, src_obj=from_obj, src_sk_name=name)
                    result[tgt_obj.name].append(new_sk.name)
            finally:
                tgt_obj.modifiers.remove(deformer)
                if active_name is not None:
                    index = tgt_obj.data.shape_keys.key_blocks.find(active_name)
                    if index >= 0:
                        active_index = index
                tgt_obj.active_shape_key_index = active_index
                tgt_obj.show_only_shape_key = show_only_shape_key

    finally:
        if noise_key is not None:
            from_obj.shape_key_remove(noise_key)

    return result
