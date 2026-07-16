import unreal

def run():
    print("---------------- INSPECTING ANIM INSTANCE PROPERTIES ----------------")
    try:
        unreal.EditorLevelLibrary.load_level("/Game/final_level")
    except Exception as e:
        print(f"Failed to load level: {e}")
        return
        
    world = unreal.EditorLevelLibrary.get_editor_world()
    actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    char_actor = None
    for actor in actors:
        if "bp_character" in actor.get_name().lower():
            char_actor = actor
            break
            
    if not char_actor:
        print("ERROR: Character actor not found")
        return
        
    face_comp = char_actor.get_editor_property("Face")
    anim_inst = face_comp.get_anim_instance()
    if not anim_inst:
        print("ERROR: AnimInstance not found")
        return
        
    # List properties
    print(f"Properties of {anim_inst.get_class().get_name()}:")
    properties = unreal.SystemLibrary.get_class_display_name(anim_inst.get_class())
    print(f"Display Name: {properties}")
    
    # We can get editor properties of the anim_inst object
    props = anim_inst.get_editor_property_names()
    matching_props = []
    for prop in props:
        # filter out standard object properties if possible, or print all
        matching_props.append(prop)
        
    print(f"Found {len(matching_props)} properties:")
    for prop in sorted(matching_props):
        try:
            val = anim_inst.get_editor_property(prop)
            # Only print if it's float or custom types
            prop_type = type(val).__name__
            # Print typical animation properties or control rig references
            if any(term in prop.lower() for term in ["ctrl", "rig", "pose", "value", "curve", "cheek", "eyelid"]):
                print(f"  - {prop} ({prop_type}): {val}")
        except Exception:
            pass

if __name__ == "__main__":
    run()
