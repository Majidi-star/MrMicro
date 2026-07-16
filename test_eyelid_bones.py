import json
import unreal

def run():
    out = ["---------------- EYELID BONE TRANSFORMS TESTING ----------------"]
    
    json_path = r"c:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\pose_interrogation_results.json"
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        out.append(f"Failed to load json: {e}")
        write_out(out)
        return
        
    seq = unreal.load_object(None, "/Game/MetaHumans/Common/Face/ARKit/AS_MetaHuman_ARKit_Mapping")
    if not seq:
        out.append("Failed to load AS_MetaHuman_ARKit_Mapping")
        write_out(out)
        return
        
    opts = unreal.AnimPoseEvaluationOptions()
    opts.evaluation_type = unreal.AnimDataEvalType.RAW
    
    target_bones = ["FACIAL_L_EyeLidLower", "FACIAL_R_EyeLidLower", "FACIAL_L_CheekOuter"]
    
    out.append("\n--- Neutral Pose ---")
    try:
        pose_neutral = unreal.AnimPoseExtensions.get_anim_pose_at_frame(seq, 0, opts)
        for b in target_bones:
            t = unreal.AnimPoseExtensions.get_bone_pose(pose_neutral, unreal.Name(b), unreal.AnimPoseSpaces.LOCAL)
            out.append(f"  {b}: {t.translation.x:.4f}, {t.translation.y:.4f}, {t.translation.z:.4f}")
    except Exception as e:
        out.append(f"Failed getting neutral: {e}")
        
    for pose_name in ["CheekSquintLeft", "CheekSquintRight", "MouthSmileLeft"]:
        if pose_name in data:
            frame = data[pose_name]["frame"]
            out.append(f"\n--- {pose_name} (Frame {frame}) ---")
            try:
                pose = unreal.AnimPoseExtensions.get_anim_pose_at_frame(seq, frame, opts)
                for b in target_bones:
                    t = unreal.AnimPoseExtensions.get_bone_pose(pose, unreal.Name(b), unreal.AnimPoseSpaces.LOCAL)
                    out.append(f"  {b}: {t.translation.x:.4f}, {t.translation.y:.4f}, {t.translation.z:.4f}")
            except Exception as e:
                out.append(f"Failed on {pose_name}: {e}")
                
    write_out(out)

def write_out(lines):
    path = r"c:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\eyelid_bone_transforms.txt"
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"Wrote {len(lines)} lines")

if __name__ == "__main__":
    run()
