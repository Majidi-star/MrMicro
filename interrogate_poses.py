import unreal
import json
import os

def run():
    print("---------------- INTERROGATING METAHUMAN ANIMS AND POSES ----------------")
    seq_path = "/Game/MetaHumans/Common/Face/ARKit/AS_MetaHuman_ARKit_Mapping"
    pose_path = "/Game/MetaHumans/Common/Face/ARKit/PA_MetaHuman_ARKit_Mapping"
    
    seq = unreal.load_object(None, seq_path)
    pose_asset = unreal.load_object(None, pose_path)
    
    if not seq or not pose_asset:
        print("ERROR: Could not load assets.")
        return
        
    pose_names = list(pose_asset.get_pose_names())
    num_frames = unreal.AnimationLibrary.get_num_frames(seq)
    print(f"Sequence frames: {num_frames}, PoseAsset poses: {len(pose_names)}")
    
    opts = unreal.AnimPoseEvaluationOptions()
    results = {}
    
    for i in range(num_frames):
        pose_name = str(pose_names[i]) if i < len(pose_names) else f"Frame_{i}"
        
        try:
            pose = unreal.AnimPoseExtensions.get_anim_pose_at_frame(seq, i, opts)
            if not unreal.AnimPoseExtensions.is_valid(pose):
                print(f"  Frame {i} ({pose_name}): Invalid pose")
                continue
                
            curves = unreal.AnimPoseExtensions.get_curve_names(pose)
            active_curves = {}
            for c in curves:
                w = unreal.AnimPoseExtensions.get_curve_weight(pose, c)
                if abs(w) > 0.001:
                    active_curves[str(c)] = float(w)
                    
            results[str(pose_name)] = {
                "frame": i,
                "time": float(unreal.AnimationLibrary.get_time_at_frame(seq, i)),
                "active_curves": active_curves
            }
            
            # Print intermediate info for key poses
            lower_name = pose_name.lower()
            if "brow" in lower_name or "cheek" in lower_name or "squint" in lower_name or "pose" in lower_name:
                print(f"Pose: '{pose_name}' (Frame {i})")
                for c, w in sorted(active_curves.items()):
                    if "ctrl" in c.lower() or "wm" in c.lower() or "brow" in c.lower() or "eye" in c.lower():
                        print(f"  - {c}: {w:.4f}")
                        
        except Exception as e:
            print(f"Error at frame {i} ({pose_name}): {e}")
            
    # Save the output to JSON
    output_path = r"c:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\pose_interrogation_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)
    print(f"\nSUCCESS: Exported interrogation data to {output_path}")

if __name__ == "__main__":
    run()
