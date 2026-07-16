import unreal

def run():
    out = []
    out.append("---------------- LEVEL SEQUENCES IN PROJECT ----------------")
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    path = unreal.TopLevelAssetPath(package_name="/Script/LevelSequence", asset_name="LevelSequence")
    filter = unreal.ARFilter(class_paths=[path], recursive_classes=True)
    assets = ar.get_assets(filter)
    out.append(f"Total Level Sequences found: {len(assets)}")
    for asset in assets:
        out.append(f"  Path: {asset.package_path}/{asset.asset_name} | Name: {asset.asset_name}")
        
    path = r"c:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\find_seqs_out.txt"
    with open(path, "w") as f:
        f.write("\n".join(out))

if __name__ == "__main__":
    run()
