import unreal
import sys

def run():
    print("---------------- INSPECTING POSE ASSET APIS ----------------")
    
    print("Help on unreal.PoseAsset:")
    try:
        # Instead of help(unreal.PoseAsset) which might be very long and write to stdout/stderr in a way that gets truncated,
        # let's list all methods and properties on the class.
        for attr in dir(unreal.PoseAsset):
            if not attr.startswith("_"):
                prop = getattr(unreal.PoseAsset, attr)
                doc = prop.__doc__ if prop.__doc__ else "No doc"
                first_line = doc.split("\n")[0] if doc else ""
                print(f"  {attr}: {first_line}")
    except Exception as e:
        print(f"Error inspecting PoseAsset: {e}")
        
    print("\nClasses in unreal containing 'Pose':")
    for name in sorted(dir(unreal)):
        if "pose" in name.lower() and not name.startswith("_"):
            try:
                cls = getattr(unreal, name)
                if isinstance(cls, type):
                    print(f"  Class: {name}")
            except:
                pass

if __name__ == "__main__":
    run()
