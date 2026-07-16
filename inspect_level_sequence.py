import unreal

def inspect_sequence(path):
    print(f"\n================ INSPECTING SEQUENCE: {path} ================")
    seq = unreal.load_object(None, path)
    if not seq:
        print("  ERROR: Could not load level sequence")
        return
        
    print(f"  Name: {seq.get_name()}")
    print(f"  Duration (frames): {seq.get_playback_end() - seq.get_playback_start() + 1}")
    print(f"  Frame Rate: {seq.get_display_rate().numerator} / {seq.get_display_rate().denominator}")
    
    bindings = seq.get_bindings()
    print(f"  Total Bindings: {len(bindings)}")
    for binding in bindings:
        name = binding.get_name()
        guid = binding.get_id()
        obj_class = binding.get_possessed_object_class()
        cls_name = obj_class.get_name() if obj_class else "None"
        print(f"    - Binding: {name} (Class: {cls_name}) | GUID: {guid}")
        
        # Tracks under this binding
        tracks = binding.get_tracks()
        print(f"      Total Tracks: {len(tracks)}")
        for track in tracks:
            print(f"        * Track: {track.get_name()} ({track.get_class().get_name()})")
            # If it's a Control Rig track, inspect section parameters
            if "ControlRig" in track.get_class().get_name():
                sections = track.get_sections()
                for section in sections:
                    print(f"          + Section: {section.get_name()}")
                    # Let's inspect animatable channels of section
                    try:
                        channels = section.get_all_channels()
                        print(f"            Total Channels: {len(channels)}")
                        # Print channels with non-empty keys
                        for chan in channels:
                            chan_name = chan.get_name()
                            num_keys = len(chan.get_keys())
                            if num_keys > 0:
                                print(f"              Channel: {chan_name} | Keys: {num_keys}")
                    except Exception as e:
                        print(f"            Failed to inspect channels: {e}")

def run():
    inspect_sequence("/Game/micro_expression")
    inspect_sequence("/Game/Mom_1_sequence")

if __name__ == "__main__":
    run()
