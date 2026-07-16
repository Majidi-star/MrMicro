import unreal

def run():
    print("---------------- FINDING ASSETS ----------------")
    
    # 1. Search for assets containing wrinkle, pose, arkit, mapping in their name
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
    assets = asset_registry.get_assets_by_path("/Game", recursive=True)
    
    match_keywords = ["wrinkle", "pose", "arkit", "mapping"]
    found_assets = []
    
    for asset in assets:
        path = str(asset.package_path) + "/" + str(asset.asset_name)
        cls = str(asset.asset_class_path.asset_name)
        path_lower = path.lower()
        if any(kw in path_lower for kw in match_keywords):
            found_assets.append((path, cls))
            
    print(f"Found {len(found_assets)} assets matching keywords:")
    for path, cls in sorted(found_assets):
        print(f"  [{cls}] {path}")
        
    # 2. Try to find the MetaHuman Face mesh and its materials
    # We can search for the Face SkeletalMesh asset
    face_meshes = []
    for asset in assets:
        cls = str(asset.asset_class_path.asset_name)
        if cls == "SkeletalMesh":
            path = str(asset.package_path) + "/" + str(asset.asset_name)
            if "face" in path.lower():
                face_meshes.append(path)
                
    print(f"\nFound Face Skeletal Meshes:")
    for mesh_path in face_meshes:
        print(f"  {mesh_path}")
        # Let's load it and inspect its materials
        mesh = unreal.load_object(None, mesh_path)
        if mesh:
            print("  Materials:")
            for i, mat_slot in enumerate(mesh.materials):
                mat_interface = mat_slot.material_interface
                if mat_interface:
                    print(f"    Slot {i} ({mat_slot.material_slot_name}): {mat_interface.get_path_name()}")
                    # print parameters if we can
                    
if __name__ == "__main__":
    run()
