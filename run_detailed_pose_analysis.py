import json
import os

def run():
    json_path = r"c:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\pose_interrogation_results.json"
    if not os.path.exists(json_path):
        print(f"ERROR: file {json_path} does not exist")
        return
        
    with open(json_path, "r") as f:
        data = json.load(f)
        
    out_lines = []
    out_lines.append(f"Loaded {len(data)} poses from json.")
    
    # 3. Corrective Shapes (Pose_4 to Pose_16)
    out_lines.append("\n================ CORRECTIVE/COMBINATION POSES ANALYSIS ================")
    for i in range(4, 18):
        pose = f"Pose_{i}"
        if pose in data:
            curves = data[pose]["active_curves"]
            out_lines.append(f"\nPose: {pose} (Frame {data[pose]['frame']})")
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
            out_lines.append("  Controls:")
            for c, w in sorted(ctrls): out_lines.append(f"    - {c}: {w:.4f}")
            out_lines.append("  Wrinkle Curves (wm):")
            for c, w in sorted(wms): out_lines.append(f"    - {c}: {w:.4f}")
            out_lines.append("  Mesh/Other Curves:")
            for c, w in sorted(mesh_curves): out_lines.append(f"    - {c}: {w:.4f}")
            
    output_file = r"c:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\pose_analysis_output.txt"
    with open(output_file, "w") as f_out:
        f_out.write("\n".join(out_lines))
    print(f"Analysis saved to {output_file}")

if __name__ == "__main__":
    run()
