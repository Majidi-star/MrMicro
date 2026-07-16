import unreal

def run():
    print("---------------- TESTING RIG COUPLING ----------------")
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
        print("ERROR: Did not find bp_character actor")
        return
        
    print(f"Found MetaHuman actor: {char_actor.get_name()}")
    
    # Get Face component
    face_comp = None
    for comp in char_actor.get_components_by_class(unreal.SkeletalMeshComponent):
        if comp.get_name() == "Face":
            face_comp = comp
            break
            
    if not face_comp:
        print("ERROR: Face SkeletalMeshComponent not found")
        return
        
    # Get AnimInstance
    anim_inst = face_comp.get_anim_instance()
    if not anim_inst:
        print("ERROR: Face component does not have AnimInstance")
        return
        
    print(f"AnimInstance: {anim_inst.get_name()} | Class: {anim_inst.get_class().get_name()}")
    
    # Try to find Control Rigs running on this AnimInstance
    try:
        rigs = unreal.ControlRigBlueprintLibrary.get_control_rigs(anim_inst)
        print(f"Found {len(rigs)} ControlRigs on Face AnimInstance:")
        for r in rigs:
            print(f"  Rig: {r.get_name()} | Class: {r.get_class().get_name()}")
            # Print available controls
            try:
                hierarchy = r.get_hierarchy()
                controls = hierarchy.get_control_keys()
                print(f"    Total Controls in RigInstance: {len(controls)}")
            except Exception as e:
                print(f"    Failed to read controls: {e}")
    except Exception as e:
        print(f"Failed to query ControlRigs: {e}")

if __name__ == "__main__":
    run()
