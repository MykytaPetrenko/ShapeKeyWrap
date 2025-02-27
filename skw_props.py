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

    delete_empty: bpy.props.BoolProperty(default=False)
    empty_threshold: bpy.props.FloatProperty(default=0.00001, precision=5)

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
