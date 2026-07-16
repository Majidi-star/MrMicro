import unreal

def run():
    asset_path = "/Game/MetaHumans/Common/Face/Face_ControlBoard_CtrlRig"
    rig_blueprint = unreal.load_object(None, asset_path)
    if not rig_blueprint:
        print("ERROR: Could not load rig blueprint")
        return
        
    hierarchy = rig_blueprint.hierarchy
    all_keys = hierarchy.get_all_keys()
    
    types = {}
    for key in all_keys:
        t_name = key.type.name
        types[t_name] = types.get(t_name, 0) + 1
        
    output_path = r"c:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\hierarchy_elements.txt"
    with open(output_path, "w") as f:
        f.write("Hierarchy elements summary:\n")
        for t, c in types.items():
            f.write(f"  {t}: {c}\n")
        f.write(f"Total elements: {len(all_keys)}\n")

if __name__ == "__main__":
    run()
