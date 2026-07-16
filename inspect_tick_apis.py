import unreal

def run():
    print("---------------- INSPECTING TICK APIS ----------------")
    
    # 1. LevelSequencePlayer methods
    print("LevelSequencePlayer methods:")
    for attr in dir(unreal.LevelSequencePlayer):
        if any(t in attr.lower() for t in ["tick", "update", "step", "force", "propagate", "evaluate"]):
            print(f"  - {attr}")
            
    # 2. World methods
    print("World methods:")
    for attr in dir(unreal.World):
        if any(t in attr.lower() for t in ["tick", "update", "step", "force"]):
            print(f"  - {attr}")
            
if __name__ == "__main__":
    run()
