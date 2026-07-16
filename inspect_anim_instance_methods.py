import unreal

def run():
    print("---------------- INSPECTING ANIM INSTANCE METHODS ----------------")
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
        
    print(f"AnimInstance class: {anim_inst.get_class().get_name()}")
    
    # Print all methods
    methods = dir(anim_inst)
    for m in sorted(methods):
        if not m.startswith("_"):
            # check if it relates to tick, eval, update, curve, pose
            print(f"  - {m}")

if __name__ == "__main__":
    run()
