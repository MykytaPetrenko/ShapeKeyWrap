import bpy
from typing import List


def _is_empty_shape_key(
        shape_key: bpy.types.ShapeKey,
        basis_shape_key: bpy.types.ShapeKey,
        empty_threshold: float
) -> bool:
    """Return whether a key differs from its Basis by no more than the threshold."""
    return all(
        (shape_key_point.co - basis_point.co).length <= empty_threshold
        for shape_key_point, basis_point in zip(shape_key.data, basis_shape_key.data)
    )


def remove_empty_shape_keys(
        context: bpy.types.Context,
        obj: bpy.types.Object,
        empty_threshold: float,
        shape_keys: List[str] | None = None
) -> int:
    """Remove empty non-Basis keys from *obj* that are in ``shape_keys``.

    Passing ``None`` scans every non-Basis key on the object; passing names
    limits the scan to those keys.  Transfer passes the keys it created or
    replaced, while the standalone Utils operator passes ``None`` unless the
    user enables Use List.

    This deliberately uses ``Object.shape_key_remove`` instead of the
    context-sensitive shape-key remove operator.  During a transfer the source
    object remains Blender's active object, so using the operator could remove
    its active key rather than the key found on ``obj``.
    """
    key_blocks = obj.data.shape_keys.key_blocks
    if len(key_blocks) <= 1:
        return 0

    basis_shape_key = key_blocks[0]
    active_shape_key = obj.active_shape_key
    active_shape_key_name = active_shape_key.name if active_shape_key else None
    shape_keys_to_remove = []

    for sk in key_blocks[1:]:
        if shape_keys is not None and sk.name not in shape_keys:
            continue

        if _is_empty_shape_key(sk, basis_shape_key, empty_threshold):
            shape_keys_to_remove.append(sk)

    for key in shape_keys_to_remove:
        obj.shape_key_remove(key)

    # Removing a preceding key can change its index.  Restore the same active
    # key by name when it was not one of the keys intentionally deleted.
    if active_shape_key_name:
        active_index = obj.data.shape_keys.key_blocks.find(active_shape_key_name)
        if active_index >= 0:
            obj.active_shape_key_index = active_index

    return len(shape_keys_to_remove)
