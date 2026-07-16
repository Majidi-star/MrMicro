import unreal

def run():
    seq_path = "/Game/MetaHumans/Common/Face/ARKit/AS_MetaHuman_ARKit_Mapping"
    seq = unreal.load_object(None, seq_path)
    if not seq:
        print("ERROR: Could not load sequence")
        return
        
    keys = unreal.AnimationLibrary.get_float_keys(seq, "browdownleft")
    if keys:
        print(f"Total keys array type: {type(keys)}")
        print(f"Total keys array length: {len(keys)}")
        
        first_item = keys[0]
        print(f"First item type: {type(first_item)}")
        
        try:
            print(f"First item length: {len(first_item)}")
            print(f"First item contents: {list(first_item)}")
        except Exception as e:
            print(f"Could not treat first item as sequence: {e}")
            
        print("\nDIR of first_item:")
        for attr in dir(first_item):
            if not attr.startswith("_"):
                print(f"  {attr}")

if __name__ == "__main__":
    run()
