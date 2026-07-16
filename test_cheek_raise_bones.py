import unreal

def run():
    out = ["---------------- TESTING BONE TRANSFORMS FOR CHEEK RAISE ----------------"]
    
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
        out.append("ERROR: bp_character not found")
        write_out(out)
        return
        
    face_comp = None
    for comp in char_actor.get_components_by_class(unreal.SkeletalMeshComponent):
        if comp.get_name() == "Face":
            face_comp = comp
            break
            
    if not face_comp:
        out.append("ERROR: Face component not found")
        write_out(out)
        return
        
    anim_inst = face_comp.get_anim_instance()
    if not anim_inst:
        out.append("ERROR: AnimInstance not found")
        write_out(out)
        return
        
    # Get the Rig
    try:
        rigs = unreal.ControlRigBlueprintLibrary.get_control_rigs(anim_inst)
    except Exception as e:
        out.append(f"ERROR getting rigs: {e}")
        write_out(out)
        return
        
    face_rig = None
    for r in rigs:
        try:
            if r.get_hierarchy().contains(unreal.RigElementKey(unreal.RigElementType.CONTROL, "CTRL_L_eye_cheekRaise")):
                face_rig = r
                break
        except Exception:
            pass
            
    if not face_rig:
        out.append("ERROR: Face Control Rig not found")
        write_out(out)
        return
        
    hierarchy = face_rig.get_hierarchy()
    
    face_comp.set_update_animation_in_editor(True)
    face_comp.set_enable_animation(True)

    test_bones = [
        "FACIAL_L_EyeLidLower",
        "FACIAL_L_EyeLidUpper",
        "FACIAL_L_CheekOuter",
        "FACIAL_L_CheekInner"
    ]
    
    ctrl = "CTRL_L_eye_cheekRaise"
    test_values = [0.0, 0.5, 1.0]
    
    for val in test_values:
        out.append(f"\n--- Setting {ctrl} = {val} ---")
        try:
            ctrl_key = unreal.RigElementKey(unreal.RigElementType.CONTROL, ctrl)
            cval = hierarchy.make_control_value_from_float(val)
            hierarchy.set_control_value(ctrl_key, cval, unreal.RigControlValueType.CURRENT)
            
            anim_inst.kismet_update_animation(0.033)
            face_comp.tick_pose(0.033, True)
            face_comp.refresh_bone_transforms()
            
            for bone in test_bones:
                bone_name = unreal.Name(bone)
                idx = face_comp.get_bone_index(bone_name)
                if idx != -1:
                    transform = face_comp.get_bone_transform(idx)
                    loc = transform.translation
                    out.append(f"  {bone} Loc: (X:{loc.x:.4f}, Y:{loc.y:.4f}, Z:{loc.z:.4f})")
                else:
                    out.append(f"  {bone} not found as bone!")
        except Exception as e:
            out.append(f"  Failed: {e}")
            
    write_out(out)

def write_out(lines):
    path = r"c:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\cheek_raise_bone_output.txt"
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"Wrote to {path}")

if __name__ == "__main__":
    run()
