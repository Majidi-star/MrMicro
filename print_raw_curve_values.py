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
        print(f"\nRAW KEYS for curve: {c}")
        try:
            keys = unreal.AnimationLibrary.get_float_keys(seq, c)
            times = keys[0]
            values = keys[1]
            print(f"Total keys: {len(times)}")
            for idx, (t, v) in enumerate(zip(times, values)):
                # Print all keys
                print(f"  [{idx}] Time={t:.4f}s (Frame {int(t*24 + 0.1)}): Value={v:.4f}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run()
