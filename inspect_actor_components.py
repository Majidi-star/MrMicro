import unreal

def run():
    print("---------------- INSPECTING ACTOR COMPONENTS ----------------")
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
        
    print(f"Actor class: {char_actor.get_class().get_name()}")
    
    # Get all components
    components = char_actor.get_components_by_class(unreal.ActorComponent)
    print(f"Found {len(components)} components:")
    for comp in components:
        comp_name = comp.get_name()
        comp_type = comp.get_class().get_name()
        print(f"  - {comp_name} ({comp_type})")

if __name__ == "__main__":
    run()
