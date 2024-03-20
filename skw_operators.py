import bpy
import mathutils
import random

REFRESH_LIST_OPTION = [
    ('REFRESH', 'Refresh', '', 0),
    ('CHECK_ALL', 'Check All', '', 1),
    ('UNCHECK_ALL', 'Uncheck All', '', 2)    
]


class IsNotBoundException(Exception):
    pass


class ObjectShapeKeyState:
    def __init__(self, obj: bpy.types.Object) -> None:
        self.show_only_shape_key = obj.show_only_shape_key
        self.shape_key_values = {sk.name: sk.value for sk in obj.data.shape_keys.key_blocks}
        self.shape_key_index = obj.active_shape_key_index

    def restore(self, obj: bpy.types.Object) -> None:
        obj.show_only_shape_key = self.show_only_shape_key
        for k, v in self.shape_key_values.items():
            sk = obj.data.shape_keys.key_blocks.get(k)
            if sk:
                sk.value = v
        obj.active_shape_key_index = self.shape_key_index


def skw_shape_key_add_binding_driver(sk, src_object: bpy.types.Object, src_sk_name: str) -> None:
    f_curve = sk.driver_add('value')
    driver = f_curve.driver
    if 'skw_var' in driver.variables:
        v = driver.variables['skw_var']
    else:
        v = driver.variables.new()
    v.type = 'SINGLE_PROP'
    v.name = 'skw_var'
    target = v.targets[0]
    target.id = src_object.id_data
    target.data_path = f'data.shape_keys.key_blocks["{src_sk_name}"].value'
    driver.expression = 'skw_var'

    f_curve = sk.driver_add('slider_min')
    driver = f_curve.driver
    if 'skw_var_min' in driver.variables:
        v = driver.variables['skw_var_min']
    else:
        v = driver.variables.new()
    v.type = 'SINGLE_PROP'
    v.name = 'skw_var_min'
    target = v.targets[0]
    target.id = src_object.id_data
    target.data_path = f'data.shape_keys.key_blocks["{src_sk_name}"].slider_min'
    driver.expression = 'skw_var_min'

    f_curve = sk.driver_add('slider_max')
    driver = f_curve.driver
    if 'skw_var_max' in driver.variables:
        v = driver.variables['skw_var_max']
    else:
        v = driver.variables.new()
    v.type = 'SINGLE_PROP'
    v.name = 'skw_var_max'
    target = v.targets[0]
    target.id = src_object.id_data
    target.data_path = f'data.shape_keys.key_blocks["{src_sk_name}"].slider_max'
    driver.expression = 'skw_var_max'


def skw_transfer_shape_keys(self, context: bpy.types.Context) -> None:
    props = self.properties
    active = context.active_object
    selected = context.selected_objects

    skw = active.data.skw_prop
    transfer_list = list()
    if skw.transfer_by_list:
        for item in skw.shape_keys_to_transfer:
            if item.checked:
                transfer_list.append(item.name)

    active_sk_state = ObjectShapeKeyState(active)
    active.show_only_shape_key = False
    for sk in active.data.shape_keys.key_blocks:
        sk.value = 0.0

    noise_key_name = None
    if skw.bind_noise:
        # Add a new shape key
        noise_key = active.shape_key_add(name="DELTA_NOISE", from_mix=False)
        noise_key_name = noise_key.name
        active.data.update()
        # Get the vertex normals from the current shape
        normals = [vertex.normal for vertex in active.data.vertices]
        # Apply random offset to each vertex in the shape key
        for i, vertex in enumerate(noise_key.data):
            offset = normals[i] * random.uniform(skw.min_noise, skw.max_noise)
            vertex.co +=  mathutils.Vector(offset)
        noise_key.value = 1.0   
    
    for target_obj in selected:
        if target_obj is active:
            continue
        target_obj_show_only_shape_key = target_obj.show_only_shape_key
        target_obj_active_shape_key_index = target_obj.active_shape_key_index
        target_obj.active_shape_key_index = 0
        target_obj.show_only_shape_key = True

        deformer = target_obj.modifiers.new(name='surface defrom', type='SURFACE_DEFORM')
        deformer.target = active
        deformer.falloff = props.falloff
        deformer.strength = props.strength
        with context.temp_override(object=target_obj):
            bpy.ops.object.modifier_move_to_index(modifier=deformer.name, index=0)
            bpy.ops.object.surfacedeform_bind(modifier=deformer.name)

        if not deformer.is_bound:
            raise IsNotBoundException()
        
        for sk in active.data.shape_keys.key_blocks[1:]:
            # Skip temp noise shape key
            if sk.name == noise_key_name:
                continue
            sk.value = 1.0
            if skw.transfer_by_list and sk.name not in transfer_list:
                continue
            deformer.name = sk.name
            if props.replace_shapekeys:
                target_sks = target_obj.data.shape_keys
                if target_sks is not None and sk.name in target_sks.key_blocks.keys():
                    sk_index = target_sks.key_blocks.keys().index(sk.name)
                    target_obj.active_shape_key_index = sk_index
                    with context.temp_override(object=target_obj):
                        bpy.ops.object.shape_key_remove()

            with context.temp_override(object=target_obj):
                bpy.ops.object.modifier_apply_as_shapekey(
                    keep_modifier=True,
                    modifier=deformer.name,
                    report=False
                )

            if props.bind:
                target_sk = target_obj.data.shape_keys.key_blocks[-1]
                skw_shape_key_add_binding_driver(
                    sk=target_sk,
                    src_object=active,
                    src_sk_name=sk.name
                )
            sk.value = 0.0
           
        target_obj.active_shape_key_index = target_obj_active_shape_key_index
        target_obj.show_only_shape_key = target_obj_show_only_shape_key
        target_obj.modifiers.remove(deformer)

    # Remove Noise Shape Key
    if noise_key_name:
        index = active.data.shape_keys.key_blocks.find(noise_key_name)
        if index > 0:
            active.active_shape_key_index = index
            bpy.ops.object.shape_key_remove()
    
    # Restore shape key values, active etc.
    active_sk_state.restore(active)
    

def skw_poll_transfer_shapekeys(context: bpy.types.Context):
    active = context.active_object
    if active is None:
        return False, 'Invalid source object'
    if active.type != 'MESH':
        return False, 'Non-mesh object is active'
    if active.data.shape_keys is None or len(active.data.shape_keys.key_blocks) <= 1:
        return False, 'Insufficient number of shapekeys'

    if len(context.selected_objects) < 2:
        return False, 'No target object selected'
    obj_count = 0
    obj_name = ''
    for obj in context.selected_objects:
        if obj.type != 'MESH':
            return False, 'Non-mesh object is selected'
        elif obj is not active:
            obj_count += 1
            obj_name = obj.name
    if obj_count == 1:
        return True, f'From: {active.name}\nTo: {obj_name}'
    else:
        return True, f'From: {active.name}\nTo: {obj_count} other objects'


def skw_bind_shape_key_values(self, context: bpy.types.Context):
    active = context.active_object
    selected = context.selected_objects

    skw = active.data.skw_prop
    transfer_list = list()
    if skw.transfer_by_list:
        for item in skw.shape_keys_to_transfer:
            if item.checked and item.name in active.data.shape_keys.key_blocks:
                transfer_list.append(item.name)
    else:
        for sk in active.data.shape_keys.key_blocks:
            transfer_list.append(sk.name)

    for target_obj in selected:
        if target_obj is active or target_obj.data.shape_keys is None:
            continue
        for sk_name in transfer_list:
            sk = target_obj.data.shape_keys.key_blocks.get(sk_name, None)
            if sk is None:
                continue
            skw_shape_key_add_binding_driver(sk=sk, src_object=active, src_sk_name=sk_name)


class SKW_OT_transfer_shape_keys(bpy.types.Operator):
    bl_idname = "shape_key_wrap.transfer"
    bl_label = "Transfer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'REGISTER', 'UNDO'}

    bind: bpy.props.BoolProperty(
        name='Bind Values',
        description='When enabled, the target shape key values and their minimum/maximum boundaries '
            'will be linked to the source shape key values using drivers.',
        default=True
    )
    replace_shapekeys: bpy.props.BoolProperty(
        name='!Replace Shapekeys',
        description='When enabled, and if the target mesh has shape keys with '
            'the same names as the source mesh, those keys will be replaced. '
            'Exercise caution when using this checkbox, as the shape key data of the target mesh '
            'could be lost irretrievably.',
            default=False
        )
    falloff: bpy.props.FloatProperty(
        name='Interpolation Falloff',
        description='Surface Deform modifier property',
        default=4, min=2, max=14)
    strength: bpy.props.FloatProperty(
        name='Strength',
        description='Surface Deform modifier property',
        default=1, min=-100, max=100
        )

    @classmethod
    def poll(cls, context):
        result, _ = skw_poll_transfer_shapekeys(context)
        return result

    def execute(self, context):
        try:
            skw_transfer_shape_keys(self, context)
        except IsNotBoundException:
            self.report({"ERROR"}, "Unable to bind surface deform modifier. Learn more from the addons github")
            return {"CANCELLED"}
        except Exception as ex:
            self.report({"ERROR"}, str(ex))
            return {"CANCELLED"}
        return {"FINISHED"}


class SKW_OT_refresh_shape_keys(bpy.types.Operator):
    bl_idname = 'shape_key_wrap.refresh_list'
    bl_label = 'Refresh'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'REGISTER', 'UNDO'}

    action: bpy.props.EnumProperty(items=REFRESH_LIST_OPTION, options={'HIDDEN'})

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        mesh = context.active_object.data
        if self.action == 'REFRESH':
            mesh.skw_prop.refresh_shape_keys(mesh, default=None)
        elif self.action == 'CHECK_ALL':
            mesh.skw_prop.refresh_shape_keys(mesh, default=True)
        elif self.action == 'UNCHECK_ALL':
            mesh.skw_prop.refresh_shape_keys(mesh, default=False)
        return {'FINISHED'}


class SKW_OT_bind_shape_key_values(bpy.types.Operator):
    bl_idname = 'shape_key_wrap.bind_values'
    bl_label = 'Bind Values'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        result, _ = skw_poll_transfer_shapekeys(context)
        return result

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        skw_bind_shape_key_values(self, context)
        return {'FINISHED'}


CLASSES = [SKW_OT_transfer_shape_keys, SKW_OT_refresh_shape_keys, SKW_OT_bind_shape_key_values]


def register():
    for c in CLASSES:
        bpy.utils.register_class(c)  


def unregister():
    for c in CLASSES:
        bpy.utils.unregister_class(c)


if __name__ == '__main__':
    register()
