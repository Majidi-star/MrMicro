import unreal

def run():
    mat_path = "/Game/MetaHumans/Common/Lookdev_UHM/Skin/Materials/M_skin_unified_baked"
    print(f"Loading Base Material: {mat_path}")
    mat = unreal.load_object(None, mat_path)
    if not mat:
        print("ERROR: Could not load master material")
        return
        
    print(f"Loaded: {mat.get_name()}")
    
    # We can inspect the material parameter names by using MaterialEditingLibrary
    # or looking at expressions
    scalar_names = unreal.MaterialEditingLibrary.get_scalar_parameter_names(mat)
    vector_names = unreal.MaterialEditingLibrary.get_vector_parameter_names(mat)
    texture_names = unreal.MaterialEditingLibrary.get_texture_parameter_names(mat)
    static_switch_names = unreal.MaterialEditingLibrary.get_static_switch_parameter_names(mat)
    
    print(f"\nScalar Parameters ({len(scalar_names)}):")
    for name in sorted(scalar_names):
        print(f"  {name}")
        
    print(f"\nVector Parameters ({len(vector_names)}):")
    for name in sorted(vector_names):
        print(f"  {name}")
        
    print(f"\nTexture Parameters ({len(texture_names)}):")
    for name in sorted(texture_names):
        print(f"  {name}")
        
    print(f"\nStatic Switch Parameters ({len(static_switch_names)}):")
    for name in sorted(static_switch_names):
        print(f"  {name}")

if __name__ == "__main__":
    run()
