import unreal

def run():
    pose_path = "/Game/MetaHumans/Common/Face/ARKit/PA_MetaHuman_ARKit_Mapping"
    pose = unreal.load_object(None, pose_path)
    if not pose:
        print("ERROR: Could not load PoseAsset")
        return
        
    print(f"Loaded PoseAsset: {pose.get_name()}")
    
    # Let's inspect the editor properties
    print("\nEditor Properties:")
    properties = [
        "source_animation",
        "pose_container",
        "base_pose_index",
        "pose_names"
    ]
    for prop in properties:
        try:
            val = pose.get_editor_property(prop)
            print(f"  {prop} = {val}")
            if prop == "pose_container":
                print(f"    pose_container dir: {dir(val)}")
                # Inspect inside pose_container
                try:
                    print(f"    pose_container.pose_data size: {len(val.pose_data)}")
                except Exception as ex:
                    print(f"    Error reading pose_container.pose_data: {ex}")
        except Exception as e:
            print(f"  Failed to read {prop}: {e}")

if __name__ == "__main__":
    run()
