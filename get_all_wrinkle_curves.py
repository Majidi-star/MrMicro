import unreal

def run():
    seq_path = "/Game/MetaHumans/Common/Face/ARKit/AS_MetaHuman_ARKit_Mapping"
    seq = unreal.load_object(None, seq_path)
    if not seq:
        print("ERROR: Could not load sequence")
        return
        
    curves = [
        "browdownleft",
        "head_wm2_normal_head_wm2_browsdown_l",
        "head_cm2_color_head_wm2_browsdown_l"
    ]
    
    for c in curves:
        print(f"\nKeys for curve: {c}")
        try:
            keys = unreal.AnimationLibrary.get_float_keys(seq, c)
            times = keys[0]
            values = keys[1]
            print(f"Found {len(times)} keys:")
            # Print first 20 non-zero keys or all if less
            count = 0
            for t, v in zip(times, values):
                if v > 0.001 or t in [0.0, 1.7083]: # Frame 0 and BrowDownLeft Pose time
                    print(f"  Time={t:.4f}s (Frame {int(t*24 + 0.1)}?): Value={v:.4f}")
                    count += 1
            if count == 0:
                print("  All key values are zero or extremely close to zero.")
        except Exception as e:
            print(f"Error querying keys for {c}: {e}")

if __name__ == "__main__":
    run()
