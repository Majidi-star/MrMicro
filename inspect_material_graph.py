import unreal

def run():
    mat_path = "/Game/MetaHumans/character/Face/Materials/MI_Face_Skin_Baked_LOD0_VT"
    print(f"Loading Material: {mat_path}")
    mat = unreal.load_object(None, mat_path)
    if not mat:
        print("Error: Could not load")
        return
        
    print(f"Material Instance: {mat.get_path_name()}")
    current = mat
    while True:
        parent = current.get_editor_property("parent") if hasattr(current, "parent") else None
        if not parent:
            # Maybe MIC's parent is reached or base material
            if hasattr(current, "get_base_material"):
                base_mat = current.get_base_material()
                print(f"Base Material: {base_mat.get_path_name()}")
            break
        print(f"-> Parent: {parent.get_path_name()} (Class: {parent.get_class().get_name()})")
        current = parent

if __name__ == "__main__":
    run()
