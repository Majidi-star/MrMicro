import unreal

def run():
    print("---------------- INSPECTING RIG HIERARCHY METHODS ----------------")
    hierarchy_class = unreal.RigHierarchy
    print("RigHierarchy methods:")
    for method in dir(hierarchy_class):
        if "value" in method.lower() or "set" in method.lower() or "control" in method.lower():
            print(f"  - {method}")

if __name__ == "__main__":
    run()
