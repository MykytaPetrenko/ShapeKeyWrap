from itertools import count
from typing import Callable

import bpy


def transfer_key_name(
        name: str,
        source_names: set[str],
        target: bpy.types.Object,
        report: Callable[[set[str], str], None] | None
) -> str:
    """Give an incoming key a distinct name if it would match the target's reference key."""
    target_keys = target.data.shape_keys
    reference_name = target_keys.reference_key.name if target_keys else "Basis"
    if name != reference_name:
        return name

    reserved_names = source_names.union(target_keys.key_blocks.keys()) if target_keys else source_names
    encoded_name = name.encode()
    for index in count():
        suffix = " (Transferred)" if index == 0 else f" (Transferred).{index:03d}"
        # Blender limits shape key names to 63 UTF-8 bytes.
        prefix = encoded_name[:63 - len(suffix)].decode(errors="ignore")
        new_name = prefix + suffix
        if new_name not in reserved_names:
            break

    if report is not None:
        report(
            {'WARNING'},
            f'{target.name}: transferring "{name}" as "{new_name}" to preserve the reference shape key.'
        )
    return new_name
