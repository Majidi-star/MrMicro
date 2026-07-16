import unreal

def run():
    seq_path = "/Game/MetaHumans/Common/Face/ARKit/AS_MetaHuman_ARKit_Mapping"
    pose_path = "/Game/MetaHumans/Common/Face/ARKit/PA_MetaHuman_ARKit_Mapping"
    
    seq = unreal.load_object(None, seq_path)
    pose = unreal.load_object(None, pose_path)
    
    if not seq or not pose:
        print("ERROR: Could not load assets")
        return
        
    num_frames = unreal.AnimationLibrary.get_num_frames(seq)
    length = unreal.AnimationLibrary.get_sequence_length(seq)
    pose_names = pose.get_pose_names()
    
    print(f"Sequence has {num_frames} frames, length: {length}s")
    print(f"Pose asset has {len(pose_names)} poses")
    
    # We want to print curve values representing how poses map to wrinkle keys
    # Let's inspect some curve values for each frame (pose)
    target_curves = [
        "browdownleft",
        "browdownright",
        "head_wm2_normal_head_wm2_browsdown_l",
        "head_wm2_normal_head_wm2_browsdown_r",
        "head_wm1_normal_head_wm1_browsraiseinner_l",
        "head_wm1_normal_head_wm1_browsraiseinner_r"
    ]
    
    for i in range(num_frames):
        time = unreal.AnimationLibrary.get_time_at_frame(seq, i)
        pose_name = pose_names[i] if i < len(pose_names) else "Unknown"
        
        print(f"\nFrame {i} at time {time:.4f}s -> Pose: {pose_name}")
        for c in target_curves:
            val = unreal.AnimationLibrary.get_float_value_at_time(seq, c, time)
            if val > 0.001:
                print(f"  Curve [{c}] = {val:.4f}")

if __name__ == "__main__":
    run()
