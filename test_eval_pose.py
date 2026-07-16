import unreal

def run():
    print("---------------- TESTING ANIM POSE EVALUATION ----------------")
    seq_path = "/Game/MetaHumans/Common/Face/ARKit/AS_MetaHuman_ARKit_Mapping"
    seq = unreal.load_object(None, seq_path)
    if not seq:
        print("ERROR: Could not load anim sequence")
        return
        
    opts = unreal.AnimPoseEvaluationOptions()
    
    # Check BrowDownLeft at frame 41
    frame = 41
    try:
        pose = unreal.AnimPoseExtensions.get_anim_pose_at_frame(seq, frame, opts)
        valid = unreal.AnimPoseExtensions.is_valid(pose)
        print(f"Pose at frame {frame} is valid: {valid}")
        if valid:
            curves = unreal.AnimPoseExtensions.get_curve_names(pose)
            print(f"Total Curves in AnimPose: {len(curves)}")
            non_zero = []
            for c in curves:
                w = unreal.AnimPoseExtensions.get_curve_weight(pose, c)
                if abs(w) > 0.001:
                    non_zero.append((str(c), w))
            print(f"Non-zero curves in pose:")
            for name, val in sorted(non_zero):
                print(f"  - {name}: {val:.4f}")
    except Exception as e:
        print(f"Failed to evaluate AnimPose: {e}")

if __name__ == "__main__":
    run()
