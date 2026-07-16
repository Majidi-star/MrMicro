import unreal

def run():
    print("---------------- ANIMATION AND SEQUENCE APIS ----------------")
    
    # 1. Search for LevelSequence Player and Editor APIs
    print("LevelSequence / MovieScene classes:")
    found_classes = []
    for attr in dir(unreal):
        if "sequence" in attr.lower() or "player" in attr.lower() or "moviescene" in attr.lower():
            try:
                cls = getattr(unreal, attr)
                if isinstance(cls, type):
                    found_classes.append(attr)
            except:
                pass
    for c in sorted(found_classes)[:40]:
        print(f"  {c}")
        
    # 2. Search for methods of interest on LevelSequencePlayer
    if hasattr(unreal, "LevelSequencePlayer"):
        print("\nMethods on unreal.LevelSequencePlayer:")
        for m in dir(unreal.LevelSequencePlayer):
            print(f"  {m}")

if __name__ == "__main__":
    run()
