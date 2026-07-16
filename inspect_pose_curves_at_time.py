import unreal

def run():
    seq_path = "/Game/MetaHumans/Common/Face/ARKit/AS_MetaHuman_ARKit_Mapping"
    seq = unreal.load_object(None, seq_path)
    if not seq:
        print("ERROR: Could not load AnimSequence")
        return
        
    # We want to check curve values at times:
    # 1.7083s (Frame 41 -> BrowDownLeft)
    # 1.7500s (Frame 42 -> BrowDownRight)
    # 1.7917s (Frame 43 -> BrowInnerUp)
    # 1.8333s (Frame 44 -> BrowOuterUpLeft)
    # 1.8750s (Frame 45 -> BrowOuterUpRight)
    # 1.9583s (Frame 47 -> CheekSquintLeft)
    
    pose_times = {
        1.7083: "BrowDownLeft",
        1.7500: "BrowDownRight",
        1.7917: "BrowInnerUp",
        1.8333: "BrowOuterUpLeft",
        1.8750: "BrowOuterUpRight",
        1.9583: "CheekSquintLeft"
    }
    
    # Get all float curves in the sequence
    curve_names = unreal.AnimationLibrary.get_animation_curve_names(seq, unreal.RawCurveTrackTypes.RCT_FLOAT)
    print(f"Total curves in sequence: {len(curve_names)}")
    
    for t, label in sorted(pose_times.items()):
        print(f"\n================ Pose: {label} (Time={t:.4f}s) ================")
        active_curves = []
        for name in curve_names:
            val = unreal.AnimationLibrary.get_float_value_at_time(seq, name, t)
            if abs(val) > 0.001:
                active_curves.append((name, val))
                
        # Sort curves by absolute value descending
        active_curves.sort(key=lambda x: abs(x[1]), reverse=True)
        for name, val in active_curves:
            print(f"  {name} = {val:.4f}")

if __name__ == "__main__":
    run()
