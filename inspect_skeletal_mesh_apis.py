import unreal

def run():
    print("---------------- SKELETAL MESH & ANIM INSTANCE APIS ----------------")
    
    comp_cls = unreal.SkeletalMeshComponent
    anim_cls = unreal.AnimInstance
    
    print("SkeletalMeshComponent methods matching tick/update/force/refresh/evaluate:")
    for method in dir(comp_cls):
        m_lower = method.lower()
        if any(w in m_lower for w in ["tick", "update", "force", "refresh", "eval", "anim"]):
            print(f"  {method}")
            
    print("\nAnimInstance methods matching tick/update/force/refresh/evaluate:")
    for method in dir(anim_cls):
        m_lower = method.lower()
        if any(w in m_lower for w in ["tick", "update", "force", "refresh", "eval"]):
            print(f"  {method}")

if __name__ == "__main__":
    run()
