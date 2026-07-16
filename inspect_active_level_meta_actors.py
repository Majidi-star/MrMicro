import unreal

def run():
    print("---------------- ACTIVE LEVEL ACTORS ----------------")
    
    # Load final_level map first
    try:
        unreal.EditorLevelLibrary.load_level("/Game/final_level")
        print("Successfully loaded /Game/final_level")
    except Exception as e:
        print(f"Failed to load level '/Game/final_level': {e}")
        
    world = unreal.EditorLevelLibrary.get_editor_world()
    if not world:
        print("ERROR: Could not get editor world")
        return
        
    actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    print(f"Total Actors: {len(actors)}")
    
    meta_actors = []
    for actor in actors:
        if "bp_character" in actor.get_name().lower() or "metahuman" in actor.get_name().lower():
            meta_actors.append(actor)
            
    print(f"Found {len(meta_actors)} MetaHuman-related actors in level:")
    for idx, actor in enumerate(meta_actors):
        print(f"\n[{idx}] Name: {actor.get_name()} | Class: {actor.get_class().get_name()}")
        
        # List components of the actor
        components = actor.get_components_by_class(unreal.ActorComponent)
        print(f"  Total Components: {len(components)}")
        for comp in components:
            comp_cls = comp.get_class().get_name()
            comp_name = comp.get_name()
            print(f"    - {comp_name} ({comp_cls})")
            
            # Find the Face SkeletalMeshComponent
            if "face" in comp_name.lower():
                skeletal_mesh_comp = comp
                # check AnimInstance
                try:
                    anim_inst = skeletal_mesh_comp.get_anim_instance()
                    if anim_inst:
                        print(f"      AnimInstance Class: {anim_inst.get_class().get_name()}")
                        print(f"      AnimInstance Outer: {anim_inst.get_outer().get_name()}")
                except Exception as ex:
                    print(f"      AnimInstance failed: {ex}")

if __name__ == "__main__":
    run()
