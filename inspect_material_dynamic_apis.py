import unreal

def run():
    print("---------------- MATERIAL DYNAMIC APIS ----------------")
    mid_cls = unreal.MaterialInstanceDynamic
    print("MaterialInstanceDynamic methods matching parameter/value/scalar:")
    for method in dir(mid_cls):
        m_lower = method.lower()
        if any(w in m_lower for w in ["param", "value", "scalar", "get"]):
            print(f"  {method}")

if __name__ == "__main__":
    run()
