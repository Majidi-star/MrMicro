import unreal

def run():
    print("---------------- INSPECTING CONTROL RIG SETTERS ----------------")
    rig_class = unreal.ControlRig
    print("ControlRig methods:")
    for method in dir(rig_class):
        if "control" in method.lower() or "value" in method.lower() or "set" in method.lower():
            print(f"  - {method}")
            
    print("\nControlRigBlueprintLibrary methods:")
    for method in dir(unreal.ControlRigBlueprintLibrary):
        if "control" in method.lower() or "value" in method.lower() or "set" in method.lower():
            print(f"  - {method}")

if __name__ == "__main__":
    run()
