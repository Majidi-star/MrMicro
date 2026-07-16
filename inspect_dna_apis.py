import unreal
import os

def run():
    out = ["---------------- INSPECTING DNA ASSET ----------------"]
    
    asset_path = "/Game/MetaHumans/Common/Face/SKM_Face_DNA.SKM_Face_DNA"
    dna_asset = unreal.load_object(None, asset_path)
    
    if not dna_asset:
        dna_asset = unreal.load_object(None, "/Game/MetaHumans/Common/Face/SKM_Face_DNA")
        
    if not dna_asset:
        out.append("ERROR: Could not load DNA asset")
        write_out(out)
        return
        
    out.append(f"Loaded DNA Asset: {dna_asset.get_name()}")
    
    out.append("\nMethods available on DNAAsset:")
    for m in dir(dna_asset):
        if not m.startswith("_"):
            out.append(f"  - {m}")
            
    out.append("\nClasses in unreal related to DNA or RigLogic:")
    for name in dir(unreal):
        if "dna" in name.lower() or "riglogic" in name.lower():
            out.append(f"  - {name}")
            
    write_out(out)

def write_out(lines):
    path = r"c:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\dna_inspection_output.txt"
    with open(path, "w") as f:
        f.write("\n".join(lines))
    print(f"Wrote to {path}")

if __name__ == "__main__":
    run()
