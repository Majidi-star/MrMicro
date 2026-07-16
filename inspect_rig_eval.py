import unreal

def run():
    print("---------------- CHECKING RIG EVALUATION ----------------")
    try:
        unreal.EditorLevelLibrary.load_level("/Game/final_level")
    except Exception as e:
        print(f"Failed to load level: {e}")
        return
        
    world = unreal.EditorLevelLibrary.get_editor_world()
    
    # Find active character actor
    actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
    print(f"Total actors in world: {len(actors)}")
    char_actor = None
    for actor in actors:
        name = actor.get_name()
        cls_name = actor.get_class().get_name()
        print(f"  Actor: {name} (Class: {cls_name})")
        if "bp_character" in name.lower():
            char_actor = actor
            
    if not char_actor:
        print("ERROR: Character actor not found!")
        return
        
    print(f"Selected Character Actor: {char_actor.get_name()}")
    face_comp = char_actor.get_editor_property("Face")
    
    # Enable animation updates in editor
    face_comp.set_update_animation_in_editor(True)
    
    # Inspect bone names
    skel = face_comp.skeletal_mesh
    num_bones = face_comp.get_num_bones()
    print(f"Face Component has {num_bones} bones")
    
    # Track some jaw/brow bones to verify movement
    test_bones = ["jaw", "head", "FRIP_L_Brow_01", "FRIP_L_Brow_02", "FACIAL_L_ForeheadActive", "FACIAL_R_ForeheadActive"]
    valid_test_bones = [b for b in test_bones if face_comp.get_bone_index(unreal.Name(b)) != -1]
    print(f"Tracing bones: {valid_test_bones}")
    
    # Load sequence
    seq_path = "/Game/micro_expression"
    seq = unreal.load_object(None, seq_path)
    settings = unreal.MovieSceneSequencePlaybackSettings()
    player, seq_actor = unreal.LevelSequencePlayer.create_level_sequence_player(world, seq, settings)
    
    def get_bone_transforms():
        t = {}
        for b in valid_test_bones:
            t[b] = face_comp.get_bone_transform_by_name(unreal.Name(b), unreal.RelativeTransformSpace.RTS_PARENT).translation
        return t

    # Capture at frame 0
    time_0 = unreal.MovieSceneSequencePlaybackParams(
        frame=unreal.FrameTime(unreal.FrameNumber(0)),
        position_type=unreal.MovieScenePositionType.FRAME,
        update_method=unreal.UpdatePositionMethod.SCRUB
    )
    player.set_playback_position(time_0)
    # Refresh mesh
    face_comp.refresh_bone_transforms()
    transforms_0 = get_bone_transforms()
    
    # Capture at frame 40 (where keys are active)
    time_40 = unreal.MovieSceneSequencePlaybackParams(
        frame=unreal.FrameTime(unreal.FrameNumber(40)),
        position_type=unreal.MovieScenePositionType.FRAME,
        update_method=unreal.UpdatePositionMethod.SCRUB
    )
    player.set_playback_position(time_40)
    face_comp.refresh_bone_transforms()
    transforms_40 = get_bone_transforms()
    
    print("\nComparing Bone Positions (Frame 0 vs Frame 40):")
    moved = False
    for b in valid_test_bones:
        p0 = transforms_0[b]
        p40 = transforms_40[b]
        dist = (p40 - p0).length()
        print(f"  {b}:")
        print(f"    Frame 0 : {p0}")
        print(f"    Frame 40: {p40}")
        print(f"    Drift   : {dist:.4f}")
        if dist > 0.001:
            moved = True
            
    if not moved:
        print("\nWARNING: None of the bones moved! Rig is not evaluating.")
    else:
        print("\nSUCCESS: Bones moved! Rig is evaluating.")

if __name__ == "__main__":
    run()
