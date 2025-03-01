import bpy
import bmesh


def find_edges_with_more_than_two_faces(mesh_object: bpy.types.Object, select: bool = False) -> int:
    if mesh_object.type != 'MESH':
        raise ValueError(f'{mesh_object.name} is not a mesh')

    bm = bmesh.new()
    bm.from_mesh(mesh_object.data)

    # Counter for issues
    invalid_edges_count = 0
    if select:
        for edge in bm.edges:
            if len(edge.link_faces) > 2:
                invalid_edges_count += 1
                edge.select_set(True)
            else:
                edge.select_set(False)
    else:
        for edge in bm.edges:
            if len(edge.link_faces) > 2:
                invalid_edges_count += 1

    if select:
        bm.to_mesh(mesh_object.data)
    bm.free()
    return invalid_edges_count


def find_concave_faces(mesh_object: bpy.types.Object, select: bool = False) -> int:
    if mesh_object.type != 'MESH':
        raise ValueError(f'{mesh_object.name} is not a mesh')

    bm = bmesh.new()
    bm.from_mesh(mesh_object.data)

    # Counter for issues
    concave_faces_count = 0

    if select:
        for face in bm.faces:
            concave = False
            for loop in face.loops:
                if not loop.is_convex:
                    concave = True
                    break
            if concave:
                concave_faces_count += 1
                face.select_set(True)
            else:
                face.select_set(False)
    else:
        for face in bm.faces:
            for loop in face.loops:
                if not loop.is_convex:
                    concave_faces_count += 1
                    break


    if select:
        bm.to_mesh(mesh_object.data)
    bm.free()
    return concave_faces_count


class SKW_OT_validate_edges(bpy.types.Operator):
    bl_idname = 'shape_key_wrap.validate_edges'
    bl_label = 'Check Edges'
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = 'Check and select edges in the active mesh object that are linked to more than two faces'


    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        if obj.type != 'MESH':
            return False
        return True
    
    def execute(self, context):
        obj = context.active_object
        invalid_edges = find_edges_with_more_than_two_faces(obj, True)
        if invalid_edges:
            self.report({'ERROR'}, f'{invalid_edges} invalid edges are found and selected. Check in Edit Mode')
        else:
            self.report({'INFO'}, 'Invalid edges are not found')
        return {'FINISHED'}
    

class SKW_OT_validate_faces(bpy.types.Operator):

    bl_idname = 'shape_key_wrap.validate_faces'
    bl_label = 'Check Concave'
    bl_description = 'Check and select concave faces in the active object.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        if obj is None:
            return False
        if obj.type != 'MESH':
            return False
        return True
    
    def execute(self, context):
        obj = context.active_object
        invalid_faces = find_concave_faces(obj, True)
        if invalid_faces:
            self.report({'ERROR'}, f'{invalid_faces} invalid faces are found and selected. Check in Edit Mode')
        else:
            self.report({'INFO'}, 'Invalid faces are not found')
        return {'FINISHED'}


def register():
    bpy.utils.register_class(SKW_OT_validate_edges)
    bpy.utils.register_class(SKW_OT_validate_faces)


def unregister():
    bpy.utils.unregister_class(SKW_OT_validate_edges)
    bpy.utils.unregister_class(SKW_OT_validate_faces)
