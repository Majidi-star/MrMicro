import unreal

def run():
    print("---------------- TESTING KISMET UPDATE TICK ----------------")
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
        
    # Load sequence
    seq_path = "/Game/micro_expression"
    seq = unreal.load_object(None, seq_path)
    if not seq:
        print("ERROR: Sequence not found")
        return
        
    # Create player
    settings = unreal.MovieSceneSequencePlaybackSettings()
    player, seq_actor = unreal.LevelSequencePlayer.create_level_sequence_player(world, seq, settings)
    if not player:
        print("ERROR: Failed to create level sequence player")
        return
        
    print("Player and bindings verified. Scrubbing to frame 30...")
    
    # Try different methods to update
    frame_num = 30
    params = unreal.MovieSceneSequencePlaybackParams(
        frame=unreal.FrameTime(unreal.FrameNumber(frame_num)),
        position_type=unreal.MovieScenePositionType.FRAME,
        update_method=unreal.UpdatePositionMethod.SCRUB
    )
    
    player.set_playback_position(params)
    
    # Try triggering update
    face_comp.set_update_animation_in_editor(True)
    face_comp.set_enable_animation(True)
    
    print("\n--- Method 1: kismet_update_animation(0.0) ---")
    anim_inst.kismet_update_animation(0.0)
    print_active_curves(anim_inst)
    
    print("\n--- Method 2: kismet_update_animation(0.033) ---")
    anim_inst.kismet_update_animation(0.033)
    print_active_curves(anim_inst)
    
    print("\n--- Method 3: reinitialize_anim_nodes() ---")
    face_comp.reinitialize_anim_nodes()
    print_active_curves(anim_inst)

def print_active_curves(anim_inst):
    # Retrieve active curve names for all types in AnimCurveType
    for type_name in dir(unreal.AnimCurveType):
        if type_name.startswith("_") or type_name in ["static_class", "cast"]:
            continue
        try:
            curve_type = getattr(unreal.AnimCurveType, type_name)
            active_names = anim_inst.get_active_curve_names(curve_type)
            print(f"CurveType {type_name}: {len(active_names)} active curves")
            non_zero = []
            for name in active_names:
                val = anim_inst.get_curve_value(name)
                if val != 0.0:
                    non_zero.append((name, val))
            if non_zero:
                for name, val in sorted(non_zero):
                    print(f"  - {name}: {val}")
        except Exception as e:
            print(f"  Failed for {type_name}: {e}")

if __name__ == "__main__":
    run()
