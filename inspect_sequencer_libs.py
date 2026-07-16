import unreal

def run():
    print("---------------- INSPECTING SEQUENCER EDITOR LIBS ----------------")
    
    # 1. LevelSequenceEditorBlueprintLibrary
    print("\nLevelSequenceEditorBlueprintLibrary methods:")
    for m in dir(unreal.LevelSequenceEditorBlueprintLibrary):
        if not m.startswith("_"):
            print(f"  LevelSequenceEditorBlueprintLibrary.{m}")
            
    # 2. LevelSequenceEditorSubsystem
    try:
        inst = unreal.get_editor_subsystem(unreal.LevelSequenceEditorSubsystem)
        print("\nLevelSequenceEditorSubsystem methods:")
        for m in dir(inst):
            if not m.startswith("_"):
                print(f"  LevelSequenceEditorSubsystem.{m}")
    except Exception as e:
        print(f"Failed to get LevelSequenceEditorSubsystem: {e}")

if __name__ == "__main__":
    run()
