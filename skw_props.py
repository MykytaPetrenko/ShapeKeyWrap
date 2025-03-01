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
    use_shape_key_list: bpy.props.BoolProperty(
        default=False,
        description=(
            'If disabled, all shape keys will be processed. '
            'If enabled, only the shape keys selected in the list at the bottom '
            'of the ShapeKeyWrap menu will be processed.'
        )
    )
    use_bind_noise: bpy.props.BoolProperty(
        default=False,
        name='Surface Deform Bind Noise',
        description=(
            "Adds random offsets to each vertex position before binding. "
            "Often helps fix the 'Unable to bind' error if no other issues exist "
            "(such as concave faces, edges with more than two faces, overlapping vertices, "
            "or faces with collinear edges)."
        )
    )
    min_noise: bpy.props.FloatProperty(
        default=-0.0001,
        name='Minimal Surface Deform Binding Noise',
        description='Lower bound for the random vertex offset used during binding.',
        precision=5
    )
    max_noise: bpy.props.FloatProperty(
        default=0.0001,
        precision=5,
        name='Maximal Surface Deform Binding Noise',
        description='Upper bound for the random vertex offset used during binding.'
    )

    show_transfer_panel: bpy.props.BoolProperty(
        default=True,
        description='Show or hide the Transfer Shape Keys panel.'
    )
    show_utilities_panel: bpy.props.BoolProperty(
        default=False,
        description='Show or hide the Utilities panel.'
    )
    show_shape_key_list_panel: bpy.props.BoolProperty(
        default=False,
        description='Show or hide the Shape Key List panel.'
    )
    
    bind_drivers: bpy.props.BoolProperty(
        name='Bind Drivers',
        description=(
            "When enabled, the addon will create drivers that link the target shape "
            "key values to the source shape key values."
        ),
        default=True
    )
    remove_empty_shape_keys: bpy.props.BoolProperty(
        name='Remove Empty ShapeKeys',
        description='When enabled, removes empty shape keys from target objects',
        default=True
    )

    empty_threshold: bpy.props.FloatProperty(
        min=0,
        default=0.00001,
        precision=5,
        description=(
            "Shape keys whose vertices do not move beyond this threshold "
            "will be considered empty and removed."
        )
    )

    overwrite_shape_keys: bpy.props.BoolProperty(
        name='!Overwrite Shapekeys',
        description= (
            "When enabled, any existing shape keys on the target mesh will be replaced "
            "by the newly transferred shape keys. If disabled, the transferred shape keys "
            "will be appended as separate shape keys (e.g., 'muscular.001'). "
            "Use with caution - this can irreversibly delete original shape key data."
        ),
        default=False
    )

    smooth_shape_keys: bpy.props.BoolProperty(
        name='Smooth Shape Keys',
        description=(
            'When enabled, apply a Corrective Smooth pass to shape keys after they are transferred.'
        ),
        default=False
    )
    sd_falloff: bpy.props.FloatProperty(
        name='Interpolation Falloff',
        description='Sets the interpolation falloff for the Surface Deform modifier.',
        default=4, min=2, max=14
    )

    sd_strength: bpy.props.FloatProperty(
        name='Strength',
        description='Controls the overall strength of the Surface Deform modifier.',
        default=1, min=-100, max=100
    )

    cs_factor: bpy.props.FloatProperty(
        name='Factor',
        description='Amount of smoothing to apply in the Corrective Smooth modifier.',
        default=0.5, min=0, max=1.0
    )

    cs_iterations: bpy.props.IntProperty(
        name='Iterations',
        description='Number of smoothing iterations to perform in the Corrective Smooth modifier.',
        default=5, min=0, max=200
    )

    cs_scale: bpy.props.FloatProperty(
        name='Scale',
        description='Scale factor used by the Corrective Smooth modifier.',
        default=1.0,
        min=0.0, max=10
    )

    cs_smooth_type: bpy.props.EnumProperty(
        items=SMOOTH_TYPES,
        name='Smooth Type',
        description='Method used for smoothing (Simple or Length Weight) in the Corrective Smooth modifier.',
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
