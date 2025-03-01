import bpy
import traceback
from .functions.bind_drivers import bind_shape_key_values, remove_shape_key_drivers
from .functions.remove_empty_shape_keys import remove_empty_shape_keys
from .functions.transfer_shape_keys import transfer_shape_keys, IsNotBoundException
from .functions.smooth_shape_keys import smooth_shape_keys


REFRESH_LIST_OPTION = [
    ('REFRESH', 'Refresh', '', 0),
    ('CHECK_ALL', 'Check All', '', 1),
    ('UNCHECK_ALL', 'Uncheck All', '', 2),
    ('INVERT', 'Invert', '', 3)
]


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


# gets called from SKW_OT_transfer_shape_keys(bpy.types.Operator):
def execute_shape_key_wrap(self, context: bpy.types.Context) -> None:
    active = context.active_object
    selected = context.selected_objects
    tgt_objs = [obj for obj in selected if obj is not active]

    skw_sk_list = active.data.skw_sk_list
    skw = context.scene.skw_prop   
    
    shape_keys = skw_sk_list.get_enabled_list() if skw.use_shape_key_list else None

    created_sks = transfer_shape_keys(
        context=context,
        from_obj=active,
        to_objs=tgt_objs,
        falloff=skw.sd_falloff,
        strength=skw.sd_strength,
        overwrite_shape_keys=skw.overwrite_shape_keys,
        shape_keys=shape_keys,
        bind_noise=(skw.min_noise, skw.max_noise) if skw.use_bind_noise else None,
        create_drivers=skw.bind_drivers
    )

    # Optionally remove empty shape keys
    if skw.remove_empty_shape_keys:
        nullshapekeysdeleted = 0
        for obj in tgt_objs:
            res = remove_empty_shape_keys(context, obj, skw.empty_threshold, shape_keys)
            nullshapekeysdeleted += res
        
        if nullshapekeysdeleted == 0:
            self.report({'INFO'}, f"No shape keys deleted. All keys have displacement above threshold.")
        else:
            self.report({'INFO'}, f"Deleted {nullshapekeysdeleted} shape keys with displacement below {skw.empty_threshold:.6f}")
            
    # Optionally smooth transferred shape keys
    if skw.smooth_shape_keys:
        for obj in tgt_objs:
            sks_to_smooth = created_sks[obj.name]
            smooth_shape_keys(
                context,
                obj,
                factor=skw.cs_factor,
                iterations=skw.cs_iterations,
                scale=skw.cs_scale,
                smooth_type=skw.cs_smooth_type,
                overwrite_shape_keys=True,
                shape_keys=sks_to_smooth
            )
    

def skw_poll(context: bpy.types.Context):
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


# gets called when transfer button clicked
class SKW_OT_transfer_shape_keys(bpy.types.Operator):
    bl_idname = "shape_key_wrap.transfer_shape_keys"
    bl_label = "Execute"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        result, _ = skw_poll(context)
        return result

    def execute(self, context):
        from_obj = context.active_object
        active_sk_state = ObjectShapeKeyState(from_obj)
        try:
            execute_shape_key_wrap(self, context)
            active_sk_state.restore(from_obj)
        except IsNotBoundException:
            # Restore shape key values, active etc.
            self.report({"ERROR"}, "Unable to bind surface deform modifier. Learn more from the addons github")
            print(traceback.format_exc())
            active_sk_state.restore(from_obj)
            return {"CANCELLED"}
        except Exception as ex:
            self.report({"ERROR"}, str(ex))
            print(traceback.format_exc())
            active_sk_state.restore(from_obj)
            return {"CANCELLED"}
        return {"FINISHED"}


class SKW_OT_refresh_shape_keys(bpy.types.Operator):
    bl_idname = 'shape_key_wrap.refresh_list'
    bl_label = 'Refresh'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_description = (
        'Shape key list operations: \n' 
        'Refresh - matches the list of transfer shape keys to the similar;\n'
        'Check All - ; \n'
        'Uncheck All - ;'
    )
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
            mesh.skw_sk_list.refresh_shape_keys(mesh, default=None)
        elif self.action == 'CHECK_ALL':
            mesh.skw_sk_list.refresh_shape_keys(mesh, default=True)
        elif self.action == 'UNCHECK_ALL':
            mesh.skw_sk_list.refresh_shape_keys(mesh, default=False)
        elif self.action == 'INVERT':
            mesh.skw_sk_list.invert_shape_keys()
        return {'FINISHED'}


class SKW_OT_bind_shape_key_values(bpy.types.Operator):
    bl_idname = 'shape_key_wrap.bind_drivers'
    bl_label = 'Bind Values Shape Keys By Name'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_description = (
        'Links shape key values and ranges of selected objects with active object '
        'by name using drivers.'
    )
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        result, _ = skw_poll(context)
        return result

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        from_obj = context.active_object
        active_sk_state = ObjectShapeKeyState(from_obj)
        try:
            active = context.active_object
            selected = context.selected_objects
            tgt_objs = [obj for obj in selected if obj is not active]

            skw_sk_list = active.data.skw_sk_list
            skw = context.scene.skw_prop

            shape_keys = skw_sk_list.get_enabled_list() if skw.use_shape_key_list else None
            
            for tgt_obj in tgt_objs:
                bind_shape_key_values(context, tgt_obj, from_obj, shape_keys)
            
            active_sk_state.restore(from_obj)
        except Exception as ex:
            self.report({"ERROR"}, str(ex))
            print(traceback.format_exc())
            active_sk_state.restore(from_obj)
            return {"CANCELLED"}
        return {"FINISHED"}
    

class SKW_OT_remove_drivers(bpy.types.Operator):
    bl_idname = 'shape_key_wrap.remove_shape_key_drivers'
    bl_label = 'Remove Shape Key Drivers'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_description = (
        'Remove drivers from shape key values and ranges from an active object'
    )
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        if obj.type != 'MESH':
            return False
        if obj.data.shape_keys is None:
            return False
        return True

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        try:
            obj = context.active_object

            skw_sk_list = obj.data.skw_sk_list
            skw = context.scene.skw_prop

            shape_keys = skw_sk_list.get_enabled_list() if skw.use_shape_key_list else None

            remove_shape_key_drivers(context, obj, shape_keys)
        except Exception as ex:
            self.report({"ERROR"}, str(ex))
            print(traceback.format_exc())
            return {"CANCELLED"}
        return {"FINISHED"}
    

class SKW_OT_remove_empty_shape_keys(bpy.types.Operator):
    bl_idname = 'shape_key_wrap.remove_empty_shape_keys'
    bl_label = 'Remove Empty Shape Keys from an active object'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_description = (
        'Remove empty shape keys'
    )
    bl_options = {'REGISTER', 'UNDO'}

    empty_threshold: bpy.props.FloatProperty(default=0.00001, precision=5)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        if obj.type != 'MESH':
            return False
        if obj.data.shape_keys is None:
            return False
        return True

    def execute(self, context):
        try:
            obj = context.active_object  

            skw_sk_list = obj.data.skw_sk_list
            skw = context.scene.skw_prop

            shape_keys = skw_sk_list.get_enabled_list() if skw.use_shape_key_list else None

            remove_empty_shape_keys(context, obj, self.empty_threshold, shape_keys)

            bpy.ops.shape_key_wrap.refresh_list(action='REFRESH')
        except Exception as ex:
            self.report({"ERROR"}, str(ex))
            print(traceback.format_exc())
            return {"CANCELLED"}
        return {"FINISHED"}
    

class SKW_OT_smooth_shape_keys(bpy.types.Operator):
    bl_idname = 'shape_key_wrap.smooth_shape_keys'
    bl_label = 'Smooth Shape Keys'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_description = (
        'Apply corrective smooth to active object shape keys'
    )
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        if obj.type != 'MESH':
            return False
        if obj.data.shape_keys is None:
            return False
        return True

    def execute(self, context):
        try:
            obj = context.active_object  

            skw_sk_list = obj.data.skw_sk_list
            skw = context.scene.skw_prop

            shape_keys = skw_sk_list.get_enabled_list() if skw.use_shape_key_list else None

            smooth_shape_keys(
                context,
                obj,
                factor=skw.cs_factor,
                iterations=skw.cs_iterations,
                scale=skw.cs_scale,
                smooth_type=skw.cs_smooth_type,
                overwrite_shape_keys=skw.overwrite_shape_keys,
                shape_keys=shape_keys
            )

            bpy.ops.shape_key_wrap.refresh_list(action='REFRESH')
        except Exception as ex:
            self.report({"ERROR"}, str(ex))
            print(traceback.format_exc())
            return {"CANCELLED"}
        return {"FINISHED"}



CLASSES = [
    SKW_OT_transfer_shape_keys,
    SKW_OT_refresh_shape_keys,
    SKW_OT_bind_shape_key_values,
    SKW_OT_remove_drivers,
    SKW_OT_remove_empty_shape_keys,
    SKW_OT_smooth_shape_keys
]


def register():
    for c in CLASSES:
        bpy.utils.register_class(c)  


def unregister():
    for c in CLASSES:
        bpy.utils.unregister_class(c)


if __name__ == '__main__':
    register()
