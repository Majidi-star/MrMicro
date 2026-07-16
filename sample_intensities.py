import unreal
import os

def run():
    out_lines = []
    out_lines.append("---------------- SAMPLING CONTROL INTENSITIES ----------------")
    try:
        unreal.EditorLevelLibrary.load_level("/Game/final_level")
    except Exception as e:
        out_lines.append(f"Failed to load level: {e}")
        write_output(out_lines)
        return
        
    world = unreal.EditorLevelLibrary.get_editor_world()
    actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    
    char_actor = None
    for actor in actors:
        if "bp_character" in actor.get_name().lower():
            char_actor = actor
            break
            
    if not char_actor:
        out_lines.append("ERROR: Did not find bp_character actor")
        write_output(out_lines)
        return
        
    face_comp = None
    for comp in char_actor.get_components_by_class(unreal.SkeletalMeshComponent):
        if comp.get_name() == "Face":
            face_comp = comp
            break
            
    if not face_comp:
        out_lines.append("ERROR: Face SkeletalMeshComponent not found")
        write_output(out_lines)
        return
        
    anim_inst = face_comp.get_anim_instance()
    if not anim_inst:
        out_lines.append("ERROR: Face component does not have AnimInstance")
        write_output(out_lines)
        return
        
    # Find the Control Rig
    rigs = []
    try:
        rigs = unreal.ControlRigBlueprintLibrary.get_control_rigs(anim_inst)
    except Exception as e:
        out_lines.append(f"Failed to query ControlRigs: {e}")
        write_output(out_lines)
        return
        
    face_rig = None
    for r in rigs:
        try:
            h = r.get_hierarchy()
            if h.contains(unreal.RigElementKey(unreal.RigElementType.CONTROL, "CTRL_L_brow_down")):
                face_rig = r
                break
        except Exception:
            pass
            
    if not face_rig:
        out_lines.append("ERROR: Could not find Face ControlRig running on AnimInstance")
        write_output(out_lines)
        return
        
    out_lines.append(f"Found Face Rig: {face_rig.get_name()}")
    hierarchy = face_rig.get_hierarchy()
    
    controls_to_test = ["CTRL_L_brow_down", "CTRL_R_brow_down"]
    
    face_comp.set_update_animation_in_editor(True)
    face_comp.set_enable_animation(True)

    intensities = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    target_wrinkle_curves = [
        "head_cm2_color_head_wm2_browsdown_l",
        "head_cm2_color_head_wm2_browsdown_r",
        "head_wm2_normal_head_wm2_browsdown_l",
        "head_wm2_normal_head_wm2_browsdown_r"
    ]
    
    for ctrl in controls_to_test:
        out_lines.append(f"\n--- Testing {ctrl} ---")
        ctrl_key = unreal.RigElementKey(unreal.RigElementType.CONTROL, ctrl)
        for intensity in intensities:
            out_lines.append(f"  Intensity: {intensity}")
            try:
                val = hierarchy.make_control_value_from_float(intensity)
                hierarchy.set_control_value(ctrl_key, val, unreal.RigControlValueType.CURRENT)
                
                anim_inst.kismet_update_animation(0.033)
                face_comp.tick_pose(0.033, True)
                face_comp.refresh_bone_transforms()
                
                for w_curve in target_wrinkle_curves:
                    w_val = anim_inst.get_curve_value(unreal.Name(w_curve))
                    out_lines.append(f"    - {w_curve}: {w_val:.4f}")
            except Exception as e:
                out_lines.append(f"    Failed at intensity {intensity}: {e}")
                
    write_output(out_lines)

def write_output(lines):
    path = r"c:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\intensity_sample_output.txt"
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"Wrote {len(lines)} lines to {path}")

if __name__ == "__main__":
    run()
