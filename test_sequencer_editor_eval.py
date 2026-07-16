import unreal

def run():
    print("---------------- TESTING SEQUENCER EDITOR EVALUATION ----------------")
    try:
        unreal.EditorLevelLibrary.load_level("/Game/final_level")
    except Exception as e:
        print(f"Failed to load level: {e}")
        return
        
    world = unreal.EditorLevelLibrary.get_editor_world()
    
    # Find active character actor
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
    print(f"Character actor: {char_actor.get_name()}")
    
    # Load LevelSequence
    seq_path = "/Game/micro_expression"
    seq = unreal.load_object(None, seq_path)
    if not seq:
        print(f"ERROR: Failed to load sequence {seq_path}")
        return
        
    # Open sequence in editor
    unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(seq)
    print("Opened level sequence in editor.")
    
    # Try different frames
    frames = [0, 15, 30, 45, 60]
    for frame in frames:
        print(f"\nSetting Sequencer time to Frame {frame}...")
        try:
            # Let's try set_current_time(frame) or set_current_local_time(frame)
            unreal.LevelSequenceEditorBlueprintLibrary.set_current_time(frame)
        except Exception as e:
            print(f"  Failed set_current_time: {e}")
            try:
                unreal.LevelSequenceEditorBlueprintLibrary.set_current_local_time(frame)
                print(f"  Succeeded set_current_local_time({frame})")
            except Exception as e2:
                print(f"  Failed set_current_local_time: {e2}")
                
        unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()
        
        # Now query curves and material parameters!
        anim_inst = face_comp.get_anim_instance()
        if anim_inst:
            curve_val = anim_inst.get_curve_value("CTRL_L_brow_raiseIn")
            print(f"  AnimInstance Curve CTRL_L_brow_raiseIn: {curve_val}")
        else:
            print("  No AnimInstance found!")
            
        mids = face_comp.get_editor_property("override_materials")
        # Let's check parameters on face_comp materials
        # Usually skeletal mesh component has override materials or active materials
        mat_instances = []
        for i in range(face_comp.get_num_materials()):
            mat = face_comp.get_material(i)
            if mat:
                mat_instances.append((i, mat))
                
        print(f"  Active Materials ({len(mat_instances)}):")
        for idx, mat in mat_instances:
            mat_name = mat.get_name()
            # If it's a MaterialInstanceDynamic or Constant
            if mat.is_a(unreal.MaterialInstanceDynamic):
                try:
                    val = mat.get_scalar_parameter_value("head_wm1_brow_in_up_l")
                    print(f"    Mat {idx} ({mat_name}) MID head_wm1_brow_in_up_l: {val}")
                except Exception as e:
                    print(f"    Mat {idx} ({mat_name}) MID error: {e}")
            elif mat.is_a(unreal.MaterialInstanceConstant) or mat.is_a(unreal.MaterialInterface):
                # Is it direct or we can get scalar override?
                # Actually during level sequence scrubbing, does the SkeletalMesh generate dynamic materials dynamically?
                # Let's check overrides or active MID on the SkeletalMeshComponent!
                pass

if __name__ == "__main__":
    run()
