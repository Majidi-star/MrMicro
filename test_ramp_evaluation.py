import unreal
import time

def run():
    out = ["---------------- TASK 8: INTERMEDIATE INTENSITIES ----------------"]
    
    # 1. Create a dummy AnimSequence
    pkg_name = "/Game/Test_Wrinkle_Ramp"
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    factory = unreal.AnimSequenceFactory()
    
    # Look for the skeleton
    skel = unreal.load_object(None, "/Game/MetaHumans/Common/Female/Medium/NormalWeight/Body/metahuman_base_skel.metahuman_base_skel")
    if not skel:
        skel = unreal.load_object(None, "/Game/MetaHumans/Common/Face/Face_Archetype_Skeleton.Face_Archetype_Skeleton")
        
    factory.target_skeleton = skel
    
    # Try creating or loading
    anim_seq = unreal.load_object(None, pkg_name)
    if not anim_seq:
        anim_seq = asset_tools.create_asset("Test_Wrinkle_Ramp", "/Game", unreal.AnimSequence, factory)
        
    if not anim_seq:
        out.append("ERROR: Could not create or load AnimSequence")
        write_out(out)
        return
        
    # Wait for curve keys to implicitly set length
    
    # 2. Add Float Curve 'browDownLeft'
    try:
        unreal.AnimationLibrary.add_curve(anim_seq, unreal.Name("browDownLeft"), unreal.RawCurveTrackTypes.RCT_FLOAT, False)
    except:
        pass # might already exist
        
    # Ramp from 0 to 1 over 1 second, with linear interpolation
    unreal.AnimationLibrary.add_float_curve_key(anim_seq, unreal.Name("browDownLeft"), 0.0, 0.0)
    unreal.AnimationLibrary.add_float_curve_key(anim_seq, unreal.Name("browDownLeft"), 0.2, 0.2)
    unreal.AnimationLibrary.add_float_curve_key(anim_seq, unreal.Name("browDownLeft"), 0.4, 0.4)
    unreal.AnimationLibrary.add_float_curve_key(anim_seq, unreal.Name("browDownLeft"), 0.6, 0.6)
    unreal.AnimationLibrary.add_float_curve_key(anim_seq, unreal.Name("browDownLeft"), 0.8, 0.8)
    unreal.AnimationLibrary.add_float_curve_key(anim_seq, unreal.Name("browDownLeft"), 1.0, 1.0)
    
    # 3. Load level and character
    unreal.EditorLevelLibrary.load_level("/Game/final_level")
    world = unreal.EditorLevelLibrary.get_editor_world()
    actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    char_actor = next((a for a in actors if "bp_character" in a.get_name().lower()), None)
    
    face_comp = next((c for c in char_actor.get_components_by_class(unreal.SkeletalMeshComponent) if c.get_name() == "Face"), None)
    anim_inst = face_comp.get_anim_instance()
    
    # 4. Play the sequence as montage or slot animation to force AnimBP evaluation
    face_comp.set_update_animation_in_editor(True)
    anim_inst.play_slot_animation_as_dynamic_montage(anim_seq, unreal.Name("DefaultSlot"), 0.0, 0.0, 1.0, 1, 0.0, 0.0)
    
    # 5. Evaluate at specific times by ticking the world/mesh
    # Instead of live ticking, we'll manually tick the scene or mesh using evaluate
    sample_times = [0.2, 0.4, 0.6, 0.8]
    
    for t in sample_times:
        anim_inst.play_slot_animation_as_dynamic_montage(anim_seq, unreal.Name("DefaultSlot"), 0.0, 0.0, 1.0, 1, 0.0, t)
        
        try:
            if hasattr(face_comp, "tick_pose"):
                face_comp.tick_pose(0.0, True)
            if hasattr(face_comp, "refresh_bone_transforms"):
                face_comp.refresh_bone_transforms()
        except:
            pass
            
        unreal.SystemLibrary.execute_console_command(world, f"t.MaxFPS 30")
        unreal.EditorLevelLibrary.editor_play_simulate() # Just to trigger internal updates? No, that runs PIE.
        
        # We can just poll the anim instance curves after forcibly setting position
        val_input = anim_inst.get_curve_value(unreal.Name("browDownLeft"))
        val_wrinkle = anim_inst.get_curve_value(unreal.Name("head_wm2_browsdown_l"))
        val_expression = anim_inst.get_curve_value(unreal.Name("ctrl_expressions_browdownl"))
        
        out.append(f"Time {t:.1f}: browDownLeft={val_input:.4f} -> Wrinkle={val_wrinkle:.4f}, Expr={val_expression:.4f}")
        
    write_out(out)

def write_out(lines):
    path = r"c:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\ramp_results.txt"
    with open(path, "w") as f:
        f.write("\n".join(lines))
        
if __name__ == "__main__":
    run()
