import unreal

def inspect_pose_asset(asset_path):
    print(f"\n================ INSPECTING POSE ASSET: {asset_path} ================")
    pose_asset = unreal.load_object(None, asset_path)
    if not pose_asset:
        print(f"Error: Could not load PoseAsset {asset_path}")
        return
        
    print(f"Class: {pose_asset.get_class().get_name()}")
    
    # Check api methods
    pose_names = []
    if hasattr(pose_asset, "get_pose_names"):
        try:
            pose_names = pose_asset.get_pose_names()
            print(f" get_pose_names() returned {len(pose_names)} poses:")
            for p in sorted(pose_names):
                print(f"    {p}")
        except Exception as e:
            print(f"  Error calling get_pose_names(): {e}")
    else:
        print("  Pose asset does not have get_pose_names attribute")
        
    # Check dir for other properties
    print("\nDIR of PoseAsset:")
    for attr in dir(pose_asset):
        if not attr.startswith("_"):
            print(f"  {attr}")

def run():
    inspect_pose_asset("/Game/MetaHumans/Common/Face/ARKit/PA_MetaHuman_ARKit_Mapping")

if __name__ == "__main__":
    run()
