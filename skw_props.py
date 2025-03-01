import bpy
from typing import List


SMOOTH_TYPES = [
    ('SIMPLE', 'Simple', 'Use the average of adjacent edge-vertices.', 1),
    ('LENGTH_WEIGHTED', 'Length Weight', 'Use the average of adjacent edge-vertices weighted by their length.', 2)
]


class SKW_ListItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default='')
    checked: bpy.props.BoolProperty(default=True)


class SKW_ShapeKeyList(bpy.types.PropertyGroup):
    shape_keys_to_process: bpy.props.CollectionProperty(type=SKW_ListItem)
    shape_key_index: bpy.props.IntProperty()

    def refresh_shape_keys(self, mesh, default=None):
        old_values = dict()
        for sk in self.shape_keys_to_process:
            old_values[sk.name] = sk.checked
        self.shape_keys_to_process.clear()
        if mesh.shape_keys is None:
            return
        for idx, sk in enumerate(mesh.shape_keys.key_blocks):
            if idx == 0:
                continue
            item = self.shape_keys_to_process.add()
            item.name = sk.name
            if default is None:
                item.checked = old_values.get(item.name, False)
            else:
                item.checked = default

    def invert_shape_keys(self):
        for sk in self.shape_keys_to_process:
            sk.checked = not sk.checked

    def get_enabled_list(self) -> List[str]:
        return [item.name for item in self.shape_keys_to_process if item.checked]


class SKW_Property(bpy.types.PropertyGroup):
    transfer_by_list: bpy.props.BoolProperty(
        default=False,
        description=(
            'If disabled, all shape keys will be processed. \n'
            'If enabled the list of shape keys to process is defined with the list of shape keys '
            'at the botom of ShapeKeyWrap menu'
        )
    )
    show_advanced: bpy.props.BoolProperty(default=False)
    bind_noise: bpy.props.BoolProperty(default=False)
    min_noise: bpy.props.FloatProperty(default=-0.0001, precision=5)
    max_noise: bpy.props.FloatProperty(default=0.0001, precision=5)

    show_transfer_block: bpy.props.BoolProperty(default=True)
    show_utils_block: bpy.props.BoolProperty(default=False)
    show_shape_key_list: bpy.props.BoolProperty(default=False)
    
    bind_values: bpy.props.BoolProperty(
        name='Bind Values',
        description=(
            'When enabled, the target shape key values and their minimum/maximum boundaries '
            'will be linked to the source shape key values using drivers'
        ),
        default=True
    )
    delete_empty: bpy.props.BoolProperty(
        name='Remove Empty ShapeKeys',
        description='When enabled, removes empty shape keys from target objects',
        default=True
    )

    empty_threshold: bpy.props.FloatProperty(default=0.00001, precision=5)

    overwrite_shapekeys: bpy.props.BoolProperty(
        name='!Overwrite Shapekeys',
        description=(
            'When enabled, and if the target mesh has shape keys with '
            'the same names as the source mesh, those keys will be replaced. '
            'Exercise caution when using this checkbox, as the shape key data of the target mesh '
            'could be lost irretrievably'
        ),
        default=False
    )

    smooth_shape_keys: bpy.props.BoolProperty(
        name='Smooth Shapekeys',
        description=(
            'When enabled, smooth shape keys after transferring using Corrective Smooth modifier'
        ),
        default=False
    )
    sd_falloff: bpy.props.FloatProperty(
        name='Interpolation Falloff',
        description='Surface Deform modifier property',
        default=4, min=2, max=14
    )

    sd_strength: bpy.props.FloatProperty(
        name='Strength',
        description='Surface Deform modifier property',
        default=1, min=-100, max=100
    )

    cs_factor: bpy.props.FloatProperty(
        name='Factor',
        description='Corrective Smooth modifier property',
        default=0.5, min=0, max=1.0
    )

    cs_iterations: bpy.props.IntProperty(
        name='Iterations',
        description='Corrective Smooth modifier property',
        default=5, min=0, max=200
    )

    cs_scale: bpy.props.FloatProperty(
        name='Scale',
        description='Corrective Smooth scale property',
        default=1.0,
        min=0.0, max=10
    )

    cs_smooth_type: bpy.props.EnumProperty(
        items=SMOOTH_TYPES,
        name='Smooth Type',
        description='Corrective Smooth method used for smoothing',
        default='SIMPLE'
    )



classes = [SKW_ListItem, SKW_Property, SKW_ShapeKeyList]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.skw_prop = bpy.props.PointerProperty(type=SKW_Property)
    bpy.types.Mesh.skw_sk_list = bpy.props.PointerProperty(type=SKW_ShapeKeyList)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    del bpy.types.Mesh.skw_sk_list
    del bpy.types.Scene.skw_prop
