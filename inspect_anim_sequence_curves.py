import unreal

def run():
    seq_path = "/Game/MetaHumans/Common/Face/ARKit/AS_MetaHuman_ARKit_Mapping"
    print(f"Loading AnimSequence: {seq_path}")
    seq = unreal.load_object(None, seq_path)
    if not seq:
        print("ERROR: Could not load anim sequence")
        return
        
    try:
        curve_names = unreal.AnimationLibrary.get_animation_curve_names(
            seq, 
            unreal.RawCurveTrackTypes.RCT_FLOAT
        )
        print(f"Found {len(curve_names)} animation curves:")
        for name in sorted(curve_names):
            print(f"  {name}")
    except Exception as e:
        print(f"Error getting curves: {e}")

if __name__ == "__main__":
    run()
