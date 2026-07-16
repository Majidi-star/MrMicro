import unreal

def run():
    print("---------------- SEARCHING UNREAL MODULE FOR SEQUENCER/EVAL APIS ----------------")
    names = dir(unreal)
    
    # Check classes with specific terms
    search_terms = ["sequencer", "levelsequence", "play", "tick", "editor"]
    matching_classes = {}
    for name in names:
        lname = name.lower()
        if any(term in lname for term in search_terms):
            try:
                obj = getattr(unreal, name)
                if isinstance(obj, type) or str(type(obj)) == "<class 'unreal.EnumClass'>":
                    matching_classes[name] = obj
            except Exception:
                pass
                
    print(f"Found {len(matching_classes)} matching classes/enums:")
    for name in sorted(matching_classes.keys()):
        # Print class/enum name and base class if it exists
        obj = matching_classes[name]
        base_name = ""
        if hasattr(obj, "__bases__") and len(obj.__bases__) > 0:
            base_name = f" (Bases: {', '.join([b.__name__ for b in obj.__bases__])})"
        print(f"  - {name}{base_name}")

if __name__ == "__main__":
    run()
