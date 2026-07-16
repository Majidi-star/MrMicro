import unreal

def run():
    mi_path = "/Game/MetaHumans/character/Face/Materials/MI_Face_Skin_Baked_LOD0_VT"
    mi = unreal.load_object(None, mi_path)
    if not mi:
        print("ERROR: Could not load MaterialInstance")
        return
        
    print(f"Loaded Material Instance: {mi.get_name()}")
    
    # Query overrides on the Material Instance
    # In UE 5.x we can use unreal.MaterialEditingLibrary or query directly
    # Since MaterialEditingLibrary is available (we used it in inspect_master_material_params.py)
    
    print("\nStatic Switch Parameter Overrides:")
    static_switches = unreal.MaterialEditingLibrary.get_static_switch_parameter_names(mi)
    for name in static_switches:
        val = unreal.MaterialEditingLibrary.get_material_instance_static_switch_parameter_value(mi, name)
        print(f"  {name} = {val}")
        
    print("\nScalar Parameter Values Set on Instance:")
    scalars = unreal.MaterialEditingLibrary.get_scalar_parameter_names(mi)
    for name in sorted(scalars):
        # We can also get value
        val = unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(mi, name)
        # Check if it contains wr or wm or head
        if "wm" in str(name).lower() or "wr" in str(name).lower() or "color" in str(name).lower():
            print(f"  {name} = {val}")

if __name__ == "__main__":
    run()
