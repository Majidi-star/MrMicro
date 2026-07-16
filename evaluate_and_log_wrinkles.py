import unreal

def run():
    out = ["---------------- EVALUATING SEQUENCE & LOGGING WRINKLES ----------------"]
    try:
        unreal.EditorLevelLibrary.load_level("/Game/final_level")
    except Exception as e:
        out.append(f"Failed to load level: {e}")
        write_out(out)
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
        
    print(f"Character Actor: {char_actor.get_name()}")
    
    face_comp = None
    for comp in char_actor.get_components_by_class(unreal.SkeletalMeshComponent):
        if comp.get_name() == "Face":
            face_comp = comp
            break
            
    if not face_comp:
        print("ERROR: Face component not found")
        return
        
    anim_inst = face_comp.get_anim_instance()
    if not anim_inst:
        print("ERROR: Face AnimInstance not found")
        return
        
    # Get sequence
    seq_path = "/Game/micro_expression"
    seq = unreal.load_object(None, seq_path)
    if not seq:
        print(f"ERROR: Could not load Level Sequence {seq_path}")
        return
        
    print(f"Loaded Level Sequence: {seq.get_name()}")
    
    # Create player
    settings = unreal.MovieSceneSequencePlaybackSettings()
    player, seq_actor = unreal.LevelSequencePlayer.create_level_sequence_player(world, seq, settings)
    if not player:
        print("ERROR: Failed to create Level Sequence Player")
        return
        
    print(f"Created LevelSequencePlayer: {player.get_name()}")
    
    # Enable animation updates in editor for commandlet evaluation
    try:
        face_comp.set_update_animation_in_editor(True)
        print("Enabled update_animation_in_editor on Face component")
    except Exception as e:
        print(f"Warning: could not set update_animation_in_editor: {e}")
        
    # Target curves to print
    target_curves = [
        "head_cm2_color_head_wm2_browsdown_l",
        "head_cm2_color_head_wm2_browsdown_r",
        "head_wm2_normal_head_wm2_browsdown_l",
        "head_wm2_normal_head_wm2_browsdown_r",
        "head_wm1_normal_head_wm1_browsup_l",
        "head_wm1_normal_head_wm1_browsup_r",
        "CTRL_L_brow_down",
        "CTRL_R_brow_down"
    ]
    
    # Target material parameters to monitor
    target_mat_params = [
        "head_wm2_normal_head_wm2_browsDown_L",
        "head_wm2_normal_head_wm2_browsDown_R",
        "head_wm1_normal_head_wm1_browsUp_L",
        "head_wm1_normal_head_wm1_browsUp_R",
        "head_cm2_color_head_wm2_browsDown_L",
        "head_cm2_color_head_wm2_browsDown_R",
        "head_cm2_color_head_wm1_browsUp_L",
        "head_cm2_color_head_wm1_browsUp_R"
    ]
    
    # Evaluate at various frames and check curves
    frames_to_test = [0, 20, 40, 60, 80, 100, 120, 140]
    for frame in frames_to_test:
        print(f"\nEvaluating Frame: {frame}")
        time_params = unreal.MovieSceneSequencePlaybackParams(
            frame=unreal.FrameTime(unreal.FrameNumber(frame)),
            position_type=unreal.MovieScenePositionType.FRAME,
            update_method=unreal.UpdatePositionMethod.SCRUB
        )
        player.set_playback_position(time_params)
        
        # Force evaluation & update
        try:
            # Recreate / update anim state
            face_comp.tick_pose(0.0, True)
            face_comp.refresh_bone_transforms()
        except Exception as e:
            print(f"  Warning on manual mesh updates: {e}")
            
        # Get curve values
        out.append(f"  AnimInstance Curve values:")
        for curve in target_curves:
            try:
                val = anim_inst.get_curve_value(unreal.Name(curve))
                out.append(f"    - {curve} = {val:.4f}")
            except Exception as e:
                out.append(f"    - {curve} = query failed: {e}")
                
        # Inspect Applied Materials
        materials = face_comp.get_materials()
        out.append(f"  Materials applied: {len(materials)}")
        for idx, mat in enumerate(materials):
            mat_cls = mat.get_class().get_name()
            # We are interested in the skin materials (slot 0 usually is LOD0 WT)
            if "Face_Skin" in mat.get_name() or idx == 0:
                out.append(f"    [{idx}] Name: {mat.get_name()} (Class: {mat_cls})")
                out.append("      Material Parameters:")
                for param in target_mat_params:
                    if isinstance(mat, unreal.MaterialInstanceDynamic):
                        try:
                            val = mat.get_scalar_parameter_value(unreal.Name(param))
                            out.append(f"        - {param} = {val:.4f}")
                        except Exception as e:
                            out.append(f"        - {param} = query failed: {e}")
                    elif isinstance(mat, unreal.MaterialInstance):
                        try:
                            val = unreal.MaterialEditingLibrary.get_material_instance_scalar_parameter_value(mat, unreal.Name(param))
                            out.append(f"        - {param} = {val:.4f}")
                        except Exception as e:
                            out.append(f"        - {param} = query failed: {e}")

    write_out(out)

def write_out(lines):
    path = r"c:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\evaluate_wrinkles_output.txt"
    with open(path, "w") as f:
        f.write("\n".join(lines))

if __name__ == "__main__":
    run()
