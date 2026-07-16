import unreal

def run():
    print("---------------- SEARCHING CONTROL RIG CLASSES ----------------")
    names = dir(unreal)
    rig_classes = []
    for name in names:
        if "controlrig" in name.lower() or "rigvm" in name.lower():
            try:
                obj = getattr(unreal, name)
                if isinstance(obj, type):
                    rig_classes.append(name)
            except Exception:
                pass
    print(f"Found {len(rig_classes)} classes:")
    for name in sorted(rig_classes):
        print(f"  - {name}")

if __name__ == "__main__":
    run()
