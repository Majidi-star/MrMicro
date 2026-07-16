import unreal

def run():
    mat_path = "/Game/MetaHumans/character/Face/Materials/MI_Face_Skin_Baked_LOD0_VT"
    print(f"Loading Material Instance: {mat_path}")
    mat = unreal.load_object(None, mat_path)
    if not mat:
        print("ERROR: Could not load material instance")
        return
        
    print("\nDIR of material instance includes:")
    for attr in dir(mat):
        if not attr.startswith("_"):
            print(f"  {attr}")
            
    print("\n--- GETTING SCALAR PARAMETERS ---")
    try:
        scalars = mat.get_editor_property("scalar_parameter_values")
        print(f"Found {len(scalars)} scalar parameter overrides:")
        for p in scalars:
            print(f"  {p.parameter_info.name} = {p.parameter_value}")
    except Exception as e:
        print(f"Error getting scalar_parameter_values: {e}")
        
    print("\n--- GETTING VECTOR PARAMETERS ---")
    try:
        vectors = mat.get_editor_property("vector_parameter_values")
        print(f"Found {len(vectors)} vector parameter overrides:")
        for p in vectors:
            val = p.parameter_value
            print(f"  {p.parameter_info.name} = ({val.r}, {val.g}, {val.b}, {val.a})")
    except Exception as e:
        print(f"Error getting vector_parameter_values: {e}")
        
    print("\n--- GETTING TEXTURE PARAMETERS ---")
    try:
        textures = mat.get_editor_property("texture_parameter_values")
        print(f"Found {len(textures)} texture parameter overrides:")
        for p in textures:
            tex = p.parameter_value
            print(f"  {p.parameter_info.name} = {tex.get_path_name() if tex else 'None'}")
    except Exception as e:
        print(f"Error getting texture_parameter_values: {e}")

if __name__ == "__main__":
    run()
