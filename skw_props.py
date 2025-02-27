import bpy


class SKW_ListItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default='')
    checked: bpy.props.BoolProperty(default=True)

class SKW_Property(bpy.types.PropertyGroup):
    shape_keys_to_transfer: bpy.props.CollectionProperty(type=SKW_ListItem)
    shape_key_index: bpy.props.IntProperty()
    transfer_by_list: bpy.props.BoolProperty(default=False)
    show_advanced: bpy.props.BoolProperty(default=False)
    bind_noise: bpy.props.BoolProperty(default=False)
    min_noise: bpy.props.FloatProperty(default=-0.0001, precision=5)
    max_noise: bpy.props.FloatProperty(default=0.0001, precision=5)

    show_transfer_block: bpy.props.BoolProperty(default=True)
    
    bind_values: bpy.props.BoolProperty(
        name='Bind Values',
        description='When enabled, the target shape key values and their minimum/maximum boundaries '
            'will be linked to the source shape key values using drivers',
        default=True
    )
    delete_empty: bpy.props.BoolProperty(
        name='Remove Empty ShapeKkeys',
        description='When enabled, removes empty shape keys from target objects',
        default=True
    )

    empty_threshold: bpy.props.FloatProperty(default=0.00001, precision=5)

    overwrite_shapekeys: bpy.props.BoolProperty(
        name='!Replace Shapekeys',
        description=(
            'When enabled, and if the target mesh has shape keys with '
            'the same names as the source mesh, those keys will be replaced. '
            'Exercise caution when using this checkbox, as the shape key data of the target mesh '
            'could be lost irretrievably'
        ),
        default=False
    )
    falloff: bpy.props.FloatProperty(
        name='Interpolation Falloff',
        description='Surface Deform modifier property',
        default=4, min=2, max=14
    )

    strength: bpy.props.FloatProperty(
        name='Strength',
        description='Surface Deform modifier property',
        default=1, min=-100, max=100
    )

    def refresh_shape_keys(self, mesh, default=None):
        old_values = dict()
        for sk in self.shape_keys_to_transfer:
            old_values[sk.name] = sk.checked
        self.shape_keys_to_transfer.clear()
        if mesh.shape_keys is None:
            return
        for idx, sk in enumerate(mesh.shape_keys.key_blocks):
            if idx == 0:
                continue
            item = self.shape_keys_to_transfer.add()
            item.name = sk.name
            if default is None:
                item.checked = old_values.get(item.name, False)
            else:
                item.checked = default


classes = [SKW_ListItem, SKW_Property]


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Mesh.skw_prop = bpy.props.PointerProperty(type=SKW_Property)


def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
    del bpy.types.Mesh.skw_prop
