import unreal

def run():
    skmesh_path = "/Game/MetaHumans/character/Face/SKM_character_FaceMesh"
    print(f"Loading Skeletal Mesh: {skmesh_path}")
    skmesh = unreal.load_object(None, skmesh_path)
    if not skmesh:
        print("ERROR: Could not load skeletal mesh")
        return
        
    skeleton = skmesh.skeleton
    print(f"Skeleton: {skeleton.get_path_name()}")
    
    # We can inspect the curve names from the skeleton's SmartNames
    # In UE 5.x, skeleton has curve names in container
    # Let's inspect all curve names from skeleton using python API
    print("\nSkeleton SmartNames / Curve Names:")
    try:
        # Get skeleton curve names
        # Let's print properties of skeleton first
        for attr in dir(skeleton):
            if "curve" in attr.lower() or "name" in attr.lower():
                print(f"  {attr}")
    except Exception as e:
        print(f"Error inspecting skeleton attributes: {e}")

if __name__ == "__main__":
    run()
