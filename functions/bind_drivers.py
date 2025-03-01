import bpy
from typing import List


def shape_key_add_binding_driver(sk, src_obj: bpy.types.Object, src_sk_name: str) -> None:
    f_curve = sk.driver_add('value')
    driver = f_curve.driver
    if 'skw_var' in driver.variables:
        v = driver.variables['skw_var']
    else:
        v = driver.variables.new()
    v.type = 'SINGLE_PROP'
    v.name = 'skw_var'
    target = v.targets[0]
    target.id = src_obj.id_data
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
    target.id = src_obj.id_data
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
    target.id = src_obj.id_data
    target.data_path = f'data.shape_keys.key_blocks["{src_sk_name}"].slider_max'
    driver.expression = 'skw_var_max'



def bind_shape_key_values(
    context: bpy.types.Context,
    tgt_obj: bpy.types.Object,
    src_obj: bpy.types.Object,
    shape_keys: List[str] | None = None
) -> None:
    if tgt_obj.data.shape_keys is None or src_obj.data.shape_keys is None:
        return
    for src_sk in src_obj.data.shape_keys.key_blocks:
        if shape_keys is not None and src_sk.name not in shape_keys:
            continue
        sk = tgt_obj.data.shape_keys.key_blocks.get(src_sk.name, None)
        if sk is None:
            continue

        shape_key_add_binding_driver(sk=sk, src_obj=src_obj, src_sk_name=src_sk.name)


def remove_shape_key_drivers(
        context: bpy.types.Context,
        obj: bpy.types.Object,
        shape_keys: List[str] | None = None
) -> None:
    if obj.data.shape_keys is None:
        # No shape keys to clear from drivers
        return
    
    for sk in obj.data.shape_keys.key_blocks:
        if shape_keys is not None and sk.name not in shape_keys:
            continue
        
        sk.driver_remove('value')
        sk.driver_remove('slider_min')
        sk.driver_remove('slider_max')
