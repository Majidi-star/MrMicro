import unreal

def run():
    print("---------------- LISTING ALL CLASS METHODS ----------------")
    
    with open("c:/Users/Amirhosein/Documents/Unreal Projects/Metahuman/tick_attribs.txt", "w") as f:
        f.write("=== unreal.LevelSequencePlayer ===\n")
        for attr in sorted(dir(unreal.LevelSequencePlayer)):
            f.write(f"{attr}\n")
            
        f.write("\n=== unreal.World ===\n")
        for attr in sorted(dir(unreal.World)):
            f.write(f"{attr}\n")
            
        f.write("\n=== unreal.GameplayStatics ===\n")
        for attr in sorted(dir(unreal.GameplayStatics)):
            f.write(f"{attr}\n")

if __name__ == "__main__":
    run()
