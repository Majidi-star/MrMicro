import unreal

def run():
    seq_path = "/Game/MetaHumans/Common/Face/ARKit/AS_MetaHuman_ARKit_Mapping"
    print(f"Loading AnimSequence: {seq_path}")
    seq = unreal.load_object(None, seq_path)
    if not seq:
        print("ERROR: Could not load anim sequence")
        return
        
    curve_names = unreal.AnimationLibrary.get_animation_curve_names(
        seq, 
        unreal.RawCurveTrackTypes.RCT_FLOAT
    )
    
    print("Filtering curves by keywords:")
    keywords = ["browsdown", "wm2", "wm1", "wm3", "brow", "wrinkle", "cheek"]
    matched = {kw: [] for kw in keywords}
    
    for name in curve_names:
        name_str = str(name).lower()
        for kw in keywords:
            if kw in name_str:
                matched[kw].append(str(name))
                
    for kw, list_names in matched.items():
        print(f"\nKeyword [{kw}] matches ({len(list_names)}):")
        # Print top 15 matches
        for m in sorted(list_names)[:15]:
            print(f"  {m}")
        if len(list_names) > 15:
            print("  ...")

if __name__ == "__main__":
    run()
