import unreal

def run():
    print("---------------- INSPECTING SKELETAL MESH COMPONENT APIS ----------------")
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
    
    # List all methods on face_comp that start with / contain refresh, update, bone, pose, anim
    keywords = ["refresh", "update", "bone", "pose", "anim"]
    methods = dir(face_comp)
    matching = []
    for m in methods:
        for kw in keywords:
            if kw in m.lower():
                matching.append(m)
                break
                
    print(f"Matching methods on SkeletalMeshComponent ({face_comp.get_class().get_name()}):")
    for m in sorted(matching):
        print(f"  - {m}")

if __name__ == "__main__":
    run()
