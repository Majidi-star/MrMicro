import unreal

def run():
    print("------------ SkeletalMeshComponent Methods ------------")
    methods = [m for m in dir(unreal.SkeletalMeshComponent) if "curve" in m.lower() or "anim" in m.lower() or "morph" in m.lower()]
    for m in methods:
        print(m)

if __name__ == "__main__":
    run()
