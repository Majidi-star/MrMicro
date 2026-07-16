import unreal

def run():
    print("---------------- INSPECTING API METHODS ----------------")
    try:
        unreal.EditorLevelLibrary.load_level("/Game/final_level")
    except Exception as e:
        print(f"Failed to load level: {e}")
        return
        
    world = unreal.EditorLevelLibrary.get_editor_world()
    
    # 1. World matching
    print("\nWorld methods matching tick/update/evaluate:")
    for m in dir(world):
        if any(x in m.lower() for x in ["tick", "update", "eval"]):
            print(f"  world.{m}")
            
    # 2. LevelSequencePlayer matching
    seq = unreal.load_object(None, "/Game/micro_expression")
    settings = unreal.MovieSceneSequencePlaybackSettings()
    player, seq_actor = unreal.LevelSequencePlayer.create_level_sequence_player(world, seq, settings)
    
    print("\nLevelSequencePlayer methods:")
    for m in dir(player):
        if any(x in m.lower() for x in ["tick", "update", "eval", "scrub", "play", "step"]):
            print(f"  player.{m}")
            
    # 3. Code search on editor subsystems
    print("\nChecking Editor Subsystems:")
    subsystems = [
        unreal.LevelEditorSubsystem,
        unreal.EditorActorSubsystem,
        unreal.UnrealEditorSubsystem
    ]
    for sub in subsystems:
        try:
            inst = unreal.get_editor_subsystem(sub)
            print(f"\n{sub.__name__} methods:")
            for m in dir(inst):
                if any(x in m.lower() for x in ["tick", "update", "force", "refresh"]):
                    print(f"  subsystem.{m}")
        except Exception as e:
            print(f"Subsystem {sub.__name__} failed: {e}")

if __name__ == "__main__":
    run()
