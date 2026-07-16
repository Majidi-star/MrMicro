import unreal

def run():
    print("Methods in unreal.ControlRigBlueprintLibrary:")
    for attr in dir(unreal.ControlRigBlueprintLibrary):
        print(f"  {attr}")
        
    print("\nSearch for control rig getter in all unreal classes:")
    for cls_name in dir(unreal):
        cls = getattr(unreal, cls_name)
        if hasattr(cls, "__bases__") and unreal.Object in cls.__bases__:
            for attr in dir(cls):
                if "control_rig" in attr.lower() or "controlrig" in attr.lower():
                    # check if it is a static method or class method
                    print(f"  {cls_name}.{attr}")

if __name__ == "__main__":
    run()
