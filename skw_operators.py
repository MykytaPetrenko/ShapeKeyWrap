import bpy


REFRESH_LIST_OPTION = [
    ('REFRESH', 'Refresh', '', 0),
    ('CHECK_ALL', 'Check All', '', 1),
    ('UNCHECK_ALL', 'Uncheck All', '', 2)    
]

def skw_shape_key_add_binding_driver(sk, src_object, src_sk_name):
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


def skw_transfer_shape_keys(self, context):
    props = self.properties
    active = context.active_object
    selected = context.selected_objects

    skw = active.data.skw_prop
    transfer_list = list()
    if skw.transfer_by_list:
        for item in skw.shape_keys_to_transfer:
            if item.checked:
                transfer_list.append(item.name)

    # Validation (Now it is done via poll classmethod)
    # if active is None or len(selected) <= 1:
    #     self.report({'ERROR'}, 'Invalid objects selection')
    #     return
    # if active.type != 'MESH':
    #     self.report({'ERROR'}, f'Valid source (active) object type is "MESH". "{active.name}" type is "{active.type}"')
    #     return
    # for obj in selected:
    #     if obj.type != 'MESH':
    #         self.report({'ERROR'}, f'Valid target object type is "MESH". "{obj.name}" type is "{obj.type}"')
    #         return
    # if active.data.shape_keys is None:
    #     self.report({'ERROR'}, f'Source (active) object "{obj.name}" does not have shape keys.')
    #     return

    active_obj_show_only_shape_key = active.show_only_shape_key
    active_obj_active_shape_key_index = active.active_shape_key_index
    active.active_shape_key_index = 0
    active.show_only_shape_key = True
    
    num_sk = len(active.data.shape_keys.key_blocks)
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
        bpy.ops.object.modifier_move_to_index(
            {"object" : target_obj},
            modifier=deformer.name, index=0
        )
        bpy.ops.object.surfacedeform_bind(
            {"object" : target_obj},
            modifier=deformer.name
        )
        
        for i in range(1, num_sk):
            active.active_shape_key_index = i
            sk = active.active_shape_key
            if skw.transfer_by_list and sk.name not in transfer_list:
                continue
            deformer.name = sk.name
            if props.replace_shapekeys:
                target_sks = target_obj.data.shape_keys
                if target_sks is not None and sk.name in target_sks.key_blocks.keys():
                    sk_index = target_sks.key_blocks.keys().index(sk.name)
                    target_obj.active_shape_key_index = sk_index
                    bpy.ops.object.shape_key_remove({"object" : target_obj})

            bpy.ops.object.modifier_apply_as_shapekey(
                {"object" : target_obj},
                keep_modifier=True,
                modifier=deformer.name, report=False
            )

            if props.bind:
                target_sk = target_obj.data.shape_keys.key_blocks[-1]
                skw_shape_key_add_binding_driver(
                    sk=target_sk,
                    src_object=active,
                    src_sk_name=sk.name
                )
           
        active.active_shape_key_index = 0

        target_obj.active_shape_key_index = target_obj_active_shape_key_index
        target_obj.show_only_shape_key = target_obj_show_only_shape_key
        target_obj.modifiers.remove(deformer)

    active.active_shape_key_index = active_obj_active_shape_key_index
    active.show_only_shape_key = active_obj_show_only_shape_key


def skw_poll_transfer_shapekeys(context):
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


def skw_bind_shape_key_values(self, context):
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
        description='If it is ON, target shape key values will be bound to source shape key values via drivers.',
        default=True
    )
    replace_shapekeys: bpy.props.BoolProperty(
        name='!Replace Shapekeys',
        description='If it is ON, and target mesh have shape key with the same names as source'
            ' mesh they will be replaced. Be carefull with the checkbox because the key shape data '
            'may be lost irrecoverably.',
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

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        skw_transfer_shape_keys(self, context)
        return {'FINISHED'}


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
