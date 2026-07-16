import json
import os

def run():
    json_path = r"c:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\pose_interrogation_results.json"
    if not os.path.exists(json_path):
        print(f"ERROR: file {json_path} does not exist")
        return
        
    with open(json_path, "r") as f:
        data = json.load(f)
        
    print(f"Loaded {len(data)} poses from json.")
    
    # 1. Brow Poses
    brow_poses = ["BrowDownLeft", "BrowDownRight", "BrowInnerUp", "BrowOuterUpLeft", "BrowOuterUpRight"]
    print("\n================ 1. BROW POSES ANALYSIS ================")
    for pose in brow_poses:
        if pose in data:
            print(f"\nPose: {pose} (Frame {data[pose]['frame']})")
            curves = data[pose]["active_curves"]
            # separate into categories
            ctrls = []
            wms = []
            lod0_mesh = []
            others = []
            for c, w in curves.items():
                if "ctrl" in c.lower():
                    ctrls.append((c, w))
                elif "wm" in c.lower():
                    wms.append((c, w))
                elif "head_lod0_mesh" in c.lower():
                    lod0_mesh.append((c, w))
                else:
                    others.append((c, w))
            print("  Controls:")
            for c, w in ctrls: print(f"    - {c}: {w:.4f}")
            print("  Wrinkle Curves (wm):")
            for c, w in wms: print(f"    - {c}: {w:.4f}")
            print("  Mesh Curves:")
            for c, w in lod0_mesh[:10]: print(f"    - {c}: {w:.4f}")
            if len(lod0_mesh) > 10: print(f"    ... and {len(lod0_mesh)-10} more mesh curves")
            if others:
                print("  Other active curves:")
                for c, w in others: print(f"      - {c}: {w:.4f}")
                
    # 2. Cheek Squint / Cheek Raise Poses
    cheek_poses = ["CheekSquintLeft", "CheekSquintRight"]
    print("\n================ 2. CHEEK AND EYE COUPLING ANALYSIS ================")
    for pose in cheek_poses:
        if pose in data:
            print(f"\nPose: {pose} (Frame {data[pose]['frame']})")
            curves = data[pose]["active_curves"]
            ctrls = []
            eye_curves = []
            wms = []
            others = []
            for c, w in curves.items():
                if "ctrl" in c.lower():
                    ctrls.append((c, w))
                elif "eye" in c.lower() or "eyelid" in c.lower() or "squint" in c.lower():
                    eye_curves.append((c, w))
                elif "wm" in c.lower():
                    wms.append((c, w))
                else:
                    others.append((c, w))
            print("  Controls:")
            for c, w in ctrls: print(f"    - {c}: {w:.4f}")
            print("  Eye/Eyelid/Squint Curves:")
            for c, w in eye_curves: print(f"    - {c}: {w:.4f}")
            print("  Wrinkle Curves (wm):")
            for c, w in wms: print(f"    - {c}: {w:.4f}")
            print("  Other curves:")
            for c, w in others[:10]: print(f"    - {c}: {w:.4f}")
            
    # 3. Corrective Shapes (Pose_4 to Pose_16)
    print("\n================ 3. CORRECTIVE/COMBINATION POSES ANALYSIS ================")
    for i in range(4, 18):
        pose = f"Pose_{i}"
        if pose in data:
            curves = data[pose]["active_curves"]
            # find non-zero curves
            print(f"\nPose: {pose} (Frame {data[pose]['frame']})")
            ctrls = []
            wms = []
            mesh_curves = []
            for c, w in curves.items():
                if "ctrl" in c.lower():
                    ctrls.append((c, w))
                elif "wm" in c.lower():
                    wms.append((c, w))
                else:
                    mesh_curves.append((c, w))
            print("  Controls:")
            for c, w in ctrls: print(f"    - {c}: {w:.4f}")
            print("  Wrinkle Curves (wm):")
            for c, w in wms: print(f"    - {c}: {w:.4f}")
            print("  Mesh/Other Curves:")
            for c, w in mesh_curves[:10]: print(f"    - {c}: {w:.4f}")

if __name__ == "__main__":
    run()
