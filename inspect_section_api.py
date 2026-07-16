import unreal

def run():
    out = ["---------------- SECTION API ----------------"]
    methods = dir(unreal.MovieSceneControlRigParameterSection)
    for m in methods:
        out.append(m)
        
    write_out(out)

def write_out(lines):
    path = r"c:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\section_apis.txt"
    with open(path, "w") as f:
        f.write("\n".join(lines))
        
if __name__ == "__main__":
    run()
