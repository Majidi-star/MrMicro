import unreal

def inspect_material(material_path):
    print(f"\n================ INSPECTING MATERIAL: {material_path} ================")
    mat = unreal.load_object(None, material_path)
    if not mat:
        print(f"Error: Could not load material {material_path}")
        return
        
    print(f"Class: {mat.get_class().get_name()}")
    
    # Trace parents
    current = mat
    while hasattr(current, "parent") and current.parent:
        print(f"  Parent: {current.parent.get_path_name()}")
        current = current.parent
        
    # Get all properties dynamically
    props = mat.get_class().get_property_names()
    print("\nMaterial Properties:")
    for prop in sorted(props):
        prop_str = str(prop)
        if any(keyword in prop_str.lower() for keyword in ["parameter", "scalar", "vector", "texture", "static", "switch"]):
            print(f"  Property: {prop_str}")
            try:
                val = mat.get_editor_property(prop_str)
                if isinstance(val, list):
                    print(f"    (List with {len(val)} items)")
                    for item in val[:10]: # Print first 10
                        if hasattr(item, "parameter_info"):
                            info = item.parameter_info
                            value = getattr(item, "parameter_value", None)
                            if value is None:
                                value = getattr(item, "value", None)
                            print(f"      {info.name} = {value}")
                        else:
                            print(f"      {item}")
                else:
                    print(f"    Value: {val}")
            except Exception as e:
                print(f"    Error reading: {e}")

def run():
    inspect_material("/Game/MetaHumans/character/Face/Materials/MI_Face_Skin_Baked_LOD0_VT")

if __name__ == "__main__":
    run()
