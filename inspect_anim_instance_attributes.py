import unreal

def run():
    print("---------------- ANIM INSTANCE INSPECTION ----------------")
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
        
    face_comp = None
    for comp in char_actor.get_components_by_class(unreal.SkeletalMeshComponent):
        if comp.get_name() == "Face":
            face_comp = comp
            break
            
    if not face_comp:
        print("ERROR: Face SkeletalMeshComponent not found")
        return
        
    anim_inst = face_comp.get_anim_instance()
    if not anim_inst:
        print("ERROR: Face component does not have AnimInstance")
        return
        
    print(f"Searching attributes on AnimInstance: {anim_inst.get_name()}")
    attrs = dir(anim_inst)
    for a in sorted(attrs):
        if not a.startswith("_"):
            print(f"  {a}")
            
    print("\nClass dir of AnimInstance:")
    for m in sorted(dir(anim_inst.get_class())):
        if not m.startswith("_"):
            print(f"  {m}")

if __name__ == "__main__":
    run()
