import unreal

def run():
    out = []
    out.append("---------------- PRINTING SEQUENCE BINDINGS ----------------")
    seq_path = "/Game/micro_expression"
    seq = unreal.load_object(None, seq_path)
    if not seq:
        out.append("ERROR: Failed to load sequence")
        write_out(out)
        return
        
    out.append(f"Sequence: {seq.get_name()}")
    bindings = seq.get_bindings()
    out.append(f"Total bindings: {len(bindings)}")
    for binding in bindings:
        name = binding.get_name()
        guid = binding.get_id().to_string()
        out.append(f"Binding: {name} (GUID: {guid})")
        tracks = binding.get_tracks()
        for t in tracks:
            out.append(f"  Track: {t.get_class().get_name()} ({t.get_name()})")
            if isinstance(t, unreal.MovieSceneControlRigParameterTrack):
                sections = t.get_sections()
                out.append(f"    Total sections: {len(sections)}")
                for sec in sections:
                    if isinstance(sec, unreal.MovieSceneControlRigParameterSection):
                        out.append(f"      Section class: {sec.get_class().get_name()}")
                        
    write_out(out)

def write_out(lines):
    path = r"c:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\print_seq_bindings_out.txt"
    with open(path, "w") as f:
        f.write("\n".join(lines))
        
if __name__ == "__main__":
    run()
