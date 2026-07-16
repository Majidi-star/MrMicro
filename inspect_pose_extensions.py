import unreal
import sys

def run():
    print("---------------- INSPECTING ANIM POSE EXTENSIONS ----------------")
    try:
        for attr in dir(unreal.AnimPoseExtensions):
            if not attr.startswith("_"):
                prop = getattr(unreal.AnimPoseExtensions, attr)
                doc = prop.__doc__ if prop.__doc__ else "No doc"
                first_line = doc.split("\n")[0] if doc else ""
                print(f"  {attr}: {first_line}")
    except Exception as e:
        print(f"Error inspecting AnimPoseExtensions: {e}")
        
    print("\n---------------- INSPECTING AnimPose ----------------")
    try:
        for attr in dir(unreal.AnimPose):
            if not attr.startswith("_"):
                prop = getattr(unreal.AnimPose, attr)
                doc = prop.__doc__ if prop.__doc__ else "No doc"
                first_line = doc.split("\n")[0] if doc else ""
                print(f"  {attr}: {first_line}")
    except Exception as e:
        print(f"Error inspecting AnimPose: {e}")

if __name__ == "__main__":
    run()
