def calculate_material(product_type_id, material_type_id, product_count, param1, param2, product_coef, defect_percent):
    if (product_count <= 0 or param1 <= 0 or param2 <= 0 or
            product_coef <= 0 or defect_percent < 0):
        return -1

    if product_type_id <= 0 or material_type_id <= 0:
        return -1

    material_per_unit = param1 * param2 * product_coef
    total_material = material_per_unit * product_count
    total_material_with_defect = total_material * (1 + defect_percent / 100)

    return int(total_material_with_defect + 0.5)