import unreal

def run():
    out = ["---------------- TASK 7: NAMESPACE CHECK ----------------"]
    try:
        unreal.EditorLevelLibrary.load_level("/Game/final_level")
    except Exception as e:
        out.append(f"Failed to load level: {e}")
        write_out(out)
        return
        
    world = unreal.EditorLevelLibrary.get_editor_world()
    actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    char_actor = next((a for a in actors if "bp_character" in a.get_name().lower()), None)
    
    if not char_actor:
        out.append("ERROR: Did not find bp_character actor")
        write_out(out)
        return
        
    face_comp = next((c for c in char_actor.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Face"), None)
    if not face_comp:
        out.append("ERROR: Face SkeletalMeshComponent not found")
        write_out(out)
        return
            
    anim_inst = face_comp.get_anim_instance()
    
    # Modify sequence
    seq_path = "/Game/micro_expression"
    seq = unreal.load_object(None, seq_path)
    if not seq:
        out.append("ERROR: Could not load sequence")
        write_out(out)
        return
        
    bindings = seq.get_bindings()
    cr_section = None
    for binding in bindings:
        for t in binding.get_tracks():
            if isinstance(t, unreal.MovieSceneControlRigParameterTrack):
                for sec in t.get_sections():
                    if isinstance(sec, unreal.MovieSceneControlRigParameterSection):
                        cr_section = sec
                        break
                        
    if not cr_section:
        out.append("ERROR: No ControlRigParameterSection found in sequence bounds.")
        write_out(out)
        return
        
    # Handle unbounded bounds
    if cr_section.has_start_frame():
        start_frame = cr_section.get_start_frame()
    else:
        start_frame = 0
        
    out.append(f"Section start bounds: {start_frame}")
    
    # Inject Keyframe at frame 10 explicitly
    time = unreal.FrameNumber(10)
    
    try:
        cr_section.add_scalar_parameter_key(unreal.Name("CTRL_L_brow_down"), time, 1.0)
        out.append("Successfully added scalar keyframe for CTRL_L_brow_down = 1.0 at Frame 0")
    except Exception as e:
        out.append(f"Failed to add keyframe: {e}")
        
    # Evaluate frame 0
    settings = unreal.MovieSceneSequencePlaybackSettings()
    player, seq_actor = unreal.LevelSequencePlayer.create_level_sequence_player(world, seq, settings)
    
    face_comp.set_update_animation_in_editor(True)
    
    time_params = unreal.MovieSceneSequencePlaybackParams(
        frame=unreal.FrameTime(time),
        position_type=unreal.MovieScenePositionType.FRAME,
        update_method=unreal.UpdatePositionMethod.SCRUB
    )
    player.set_playback_position(time_params)
    
    try:
        if hasattr(face_comp, "tick_pose"):
            face_comp.tick_pose(0.0, True)
        if hasattr(face_comp, "refresh_bone_transforms"):
            face_comp.refresh_bone_transforms()
    except Exception as e:
        out.append(f"Warning on manual mesh updates: {e}")
    
    out.append("\nResults after keyframing:")
    target_curves = ["head_wm2_browsdown_l", "head_wm2_normal_head_wm2_browsdown_l", "ctrl_expressions_browdownl"]
    for c in target_curves:
        try:
            val = anim_inst.get_curve_value(unreal.Name(c))
            out.append(f"  {c} = {val:.4f}")
        except Exception as e:
            out.append(f"  {c} = query failed: {e}")
            
    # Also verify the input got mapped correctly to RigLogic
    try:
        val = anim_inst.get_curve_value(unreal.Name("CTRL_L_brow_down"))
        out.append(f"  CTRL_L_brow_down (Readback) = {val:.4f}")
    except:
        pass
        
    write_out(out)

def write_out(lines):
    path = r"c:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\namespace_check_output.txt"
    with open(path, "w") as f:
        f.write("\n".join(lines))
        
if __name__ == "__main__":
    run()
