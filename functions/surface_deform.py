import bpy
import bmesh
import math
from typing import List
from mathutils.bvhtree import BVHTree
from mathutils import Vector
from mathutils.kdtree import KDTree


def create_surface_binding(src_obj: bpy.types.Object, tgt_obj: bpy.types.Object):
    """
    Bind target mesh vertices to the nearest source mesh triangle using BVHTree.

    This function binds each vertex of the target mesh to the closest triangle 
    on the source mesh. It uses the BVHTree structure for efficient nearest 
    neighbor search and calculates the barycentric coordinates of each binding.

    Args:
        src_obj (bpy.types.Object): The source object whose mesh will be used for binding.
        tgt_obj (bpy.types.Object): The target object whose vertices will be bound to the source mesh.

    Returns:
        list: A list of tuples containing binding data for each target vertex.
              Each tuple consists of:
              - vertex_indices (list of int): Indices of the vertices of the closest triangle in the source mesh.
              - normal (Vector): Normal of the closest triangle face.
              - b_coords (tuple of float): Barycentric coordinates of the target vertex relative to the closest triangle.
              - offset (float): Distance from the target vertex to the triangle plane along the normal.
    """
    source_mesh: bpy.types.Mesh = src_obj.data
    target_mesh: bpy.types.Mesh = tgt_obj.data

    if target_mesh.shape_keys and len(target_mesh.shape_keys.key_blocks) >= 1:
        target_verts = target_mesh.shape_keys.key_blocks[0].data
    else:
        target_verts = target_mesh.vertices

    bm = bmesh.new()
    bm.from_mesh(source_mesh)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.faces.ensure_lookup_table()
    bm.normal_update()
    bvh = BVHTree.FromBMesh(bm, epsilon=0.0001)

    # Barycentric coordinates helper function
    def barycentric_coords(pt, v1, v2, v3):
        v2_v1 = v2 - v1
        v3_v1 = v3 - v1
        pt_v1 = pt - v1
        d00 = v2_v1.dot(v2_v1)
        d01 = v2_v1.dot(v3_v1)
        d11 = v3_v1.dot(v3_v1)
        d20 = pt_v1.dot(v2_v1)
        d21 = pt_v1.dot(v3_v1)
        denom = d00 * d11 - d01 * d01
        v = (d11 * d20 - d01 * d21) / denom
        w = (d00 * d21 - d01 * d20) / denom
        u = 1.0 - v - w
        return (u, v, w)

    # Bind each target vertex to the closest source triangle
    bind_data = []
    for v in target_verts:
        _, normal, index, _ = bvh.find_nearest(v.co)
        if index is not None:
            face = bm.faces[index]
            verts = [vert.co for vert in face.verts]
            vertex_indices = [vert.index for vert in face.verts]
            if face.normal.length <= 0.5:
                print(face.normal)
            b_coords = barycentric_coords(v.co, *verts)
            offset = (v.co - (verts[0] * b_coords[0] + verts[1] * b_coords[1] + verts[2] * b_coords[2])).dot(normal)
            bind_data.append((vertex_indices, face.normal.copy(), b_coords, offset))
            
        else:
            raise Exception

    bm.free()  # Free the BMesh

    return bind_data


def calc_surface_deform(
        bind_data,
        new_source_data: list
) -> None:
    """
    Identify problem vertices based on angular deviation of binding normals.

    This function identifies vertices in the target mesh that may have problematic 
    bindings based on the angular deviation of the normals of their associated triangles 
    in the binding data. Vertices with an average normal deviation above a specified 
    threshold are flagged as problem vertices.

    Args:
        target_obj (bpy.types.Object): The target object whose vertices are being analyzed.
        bind_data (dict): Binding data for the target vertices. Each entry is a tuple containing
                          the vertex indices, normal, barycentric coordinates, and offset.

    Returns:
        dict: A dictionary where the keys are vertex indices and the values are the 
              normalized problem severity (ranging from 0.0 to 1.0).
    """
    
    new_co = list()
    # Apply deformations
    for vertices, normal, b_coords, offset in bind_data:

        verts = [new_source_data[idx] for idx in vertices]
        new_pos = verts[0] * b_coords[0] + verts[1] * b_coords[1] + verts[2] * b_coords[2]
        new_pos += normal * offset
        new_co.append(new_pos)
    return new_co


def transfer_shapekeys(
        context: bpy.types.Context,
        tgt_obj: bpy.types.Object,
        src_obj: bpy.types.Object,
        shape_keys: List[str] | None = None,
        overwrite_shape_keys: bool = False
    ) -> List[str]:
    """
    Transfer shape keys from source objects to target objects.

    This function transfers shape key deformations from source objects to target objects.
    It can optionally apply corrective smoothing iterations to address any problematic
    vertex bindings.

    Args:
        context (bpy.types.Context): The current context in Blender.
        target_objects (bpy.types.Object): A tuple of target basis and target final objects.
        source_objects (bpy.types.Object): A tuple of source basis and source final objects.
        basis_shape_key (str, optional): The name of the basis shape key to use. Defaults to None.
        shape_keys (List[str], optional): A list of shape key names to transfer. Defaults to None.

    Returns:
        None

    Raises:
        Exception: If the target shape key is not found in the source object.
        ValueError: If there is a mismatch in the number of vertices.
    """
    binding = create_surface_binding(src_obj, tgt_obj)
    new_sks = []

    if shape_keys is None:
        # Process all shape keys
        shape_keys = [sk.name for sk in src_obj.data.shape_keys.key_blocks[1:]]
    
    for sk_name in shape_keys:
        sk = src_obj.data.shape_keys.key_blocks.get(sk_name)
        if not sk:
            continue
        
        new_coordinates = calc_surface_deform(binding, [v.co for v in sk.data])

        if tgt_obj.data.shape_keys is None:
            tgt_obj.shape_key_add(name="Basis", from_mix=False)
            tgt_sk = tgt_obj.shape_key_add(name=sk_name, from_mix=False)
        else:
            tgt_sk = tgt_obj.data.shape_keys.key_blocks.get(sk_name)
            if tgt_sk is None or not overwrite_shape_keys:
                tgt_sk = tgt_obj.shape_key_add(name=sk_name, from_mix=False)

        flattened_coordinates = [value for co in new_coordinates for value in co[:]]
        # Ensure the length matches
        if len(flattened_coordinates) == 3 * len(tgt_sk.data):
            tgt_sk.data.foreach_set("co", flattened_coordinates)
        else:
            raise ValueError("Mismatch in the number of vertices.")

        new_sks.append(tgt_sk.name)
    return new_sks
