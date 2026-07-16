import unreal

def run():
    seq_path = "/Game/MetaHumans/Common/Face/ARKit/AS_MetaHuman_ARKit_Mapping"
    seq = unreal.load_object(None, seq_path)
    if not seq:
        print("ERROR: Could not load sequence")
        return
        
    curves = [
        "browdownleft",
        "head_wm2_normal_head_wm2_browsdown_l"
    ]
    
    for c in curves:
        print(f"\nKeys for curve: {c}")
        try:
            # We can use AnimationLibrary.get_float_keys
            keys = unreal.AnimationLibrary.get_float_keys(seq, c)
            print(f"Found {len(keys)} keys:")
            for k in keys:
                print(f"  Time={k.time:.4f}, Value={k.value:.4f}")
        except Exception as e:
            print(f"Error querying keys: {e}")

if __name__ == "__main__":
    run()
