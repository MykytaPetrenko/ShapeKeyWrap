import bpy
import traceback
from .functions.bind_drivers import bind_shape_key_values
from .functions.remove_empty import remove_empty_shape_keys
from .functions.transfer_shape_keys import transfer_shape_keys, IsNotBoundException


REFRESH_LIST_OPTION = [
    ('REFRESH', 'Refresh', '', 0),
    ('CHECK_ALL', 'Check All', '', 1),
    ('UNCHECK_ALL', 'Uncheck All', '', 2)    
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

    skw = active.data.skw_prop    
    
    if skw.transfer_by_list:
        transfer_list = [item.name for item in skw.shape_keys_to_transfer if item.checked]
    else:
        transfer_list = None

    transfer_shape_keys(
        context=context,
        from_obj=active,
        to_objs=tgt_objs,
        falloff=skw.falloff,
        strength=skw.strength,
        replace_existing_shape_keys=skw.overwrite_shapekeys,
        transfer_list=transfer_list,
        bind_noise=(skw.min_noise, skw.max_noise) if skw.bind_noise else None
    )

    # Optionally remove empty shape keys
    if skw.delete_empty:
        nullshapekeysdeleted = 0
        for obj in tgt_objs:
            res = remove_empty_shape_keys(context, obj, skw.empty_threshold, transfer_list)
            nullshapekeysdeleted += res
        
        if nullshapekeysdeleted == 0:
            self.report({'INFO'}, f"No shape keys deleted. All keys have displacement above threshold.")
        else:
            self.report({'INFO'}, f"Deleted {nullshapekeysdeleted} shape keys with displacement below {skw.empty_threshold:.6f}")
            
    # Optionally link the values and ranges of the transferred shape keys to the source
    if skw.bind_values:
        for obj in tgt_objs:
            bind_shape_key_values(context, obj, active, transfer_list)
    

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
    bl_idname = "shape_key_wrap.execute"
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
        bind_shape_key_values(self, context)
        return {'FINISHED'}


CLASSES = [SKW_OT_transfer_shape_keys, SKW_OT_refresh_shape_keys]


def register():
    for c in CLASSES:
        bpy.utils.register_class(c)  


def unregister():
    for c in CLASSES:
        bpy.utils.unregister_class(c)


if __name__ == '__main__':
    register()
