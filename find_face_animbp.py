import unreal

def run():
    print("---------------- FINDING FACE ANIM SYSTEM ----------------")
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = asset_registry.get_assets_by_path("/Game", recursive=True)
    
    # List anim blueprints
    anim_bps = []
    mpcs = []
    pose_assets = []
    
    for asset in assets:
        cls = str(asset.asset_class_path.asset_name)
        path = str(asset.package_path) + "/" + str(asset.asset_name)
        if cls == "AnimBlueprint":
            if "face" in path.lower() or "character" in path.lower():
                anim_bps.append(path)
        elif cls == "MaterialParameterCollection":
            mpcs.append(path)
        elif cls == "PoseAsset":
            pose_assets.append(path)
            
    print(f"\nAnim Blueprints ({len(anim_bps)}):")
    for bp in anim_bps:
        print(f"  {bp}")
        
    print(f"\nMaterial Parameter Collections ({len(mpcs)}):")
    for mpc in mpcs:
        print(f"  {mpc}")
        
    print(f"\nPose Assets ({len(pose_assets)}):")
    for pa in pose_assets:
        print(f"  {pa}")

if __name__ == "__main__":
    run()
