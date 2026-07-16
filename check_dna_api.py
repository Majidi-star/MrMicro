import unreal

def run():
    out = ["---------------- TASK 9: OPEN RIG LOGIC PYTHON API ----------------"]
    out.append("Checking RigLogic availability in Unreal Python API...")
    
    has_dna = hasattr(unreal, 'DNAAsset')
    out.append(f"unreal.DNAAsset available: {has_dna}")
    
    if has_dna:
        out.append("\nMethods and properties of unreal.DNAAsset:")
        for name in dir(unreal.DNAAsset):
            if not name.startswith('_'):
                out.append(f"  {name}")
                
    has_rig_logic = hasattr(unreal, 'RigLogic')
    out.append(f"\nunreal.RigLogic available: {has_rig_logic}")
    
    if has_rig_logic:
        out.append("\nMethods and properties of unreal.RigLogic:")
        for name in dir(unreal.RigLogic):
            if not name.startswith('_'):
                out.append(f"  {name}")
                
    has_riglogic_module = False
    try:
        import riglogic
        has_riglogic_module = True
    except:
        pass
        
    out.append(f"\nStandalone 'riglogic' python module available: {has_riglogic_module}")
    if has_riglogic_module:
        import riglogic
        out.append(f"  Standalone 'riglogic' dir: {dir(riglogic)}")

    path = r"c:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\dna_api_out.txt"
    with open(path, "w") as f:
        f.write("\n".join(out))

if __name__ == "__main__":
    run()
