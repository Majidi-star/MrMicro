import unreal

def run():
    print("---------------- SEARCHING FOR TICK OR UPDATE IN UNREAL MODULE ----------------")
    names = dir(unreal)
    tick_items = []
    update_items = []
    
    for name in names:
        lname = name.lower()
        if "tick" in lname:
            tick_items.append(name)
        elif "update" in lname:
            update_items.append(name)
            
    print(f"Tick items ({len(tick_items)}):")
    for item in sorted(tick_items)[:100]:
        print(f"  - {item}")
        
    print(f"\nUpdate items ({len(update_items)}):")
    for item in sorted(update_items)[:100]:
        print(f"  - {item}")

if __name__ == "__main__":
    run()
