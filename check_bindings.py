import unreal

def run():
    print("---------------- CHECK BOUND SEQUENCE OBJECTS ----------------")
    try:
        unreal.EditorLevelLibrary.load_level("/Game/final_level")
    except Exception as e:
        print(f"Failed to load level: {e}")
        return
        
    world = unreal.EditorLevelLibrary.get_editor_world()
    
    seq_path = "/Game/micro_expression"
    seq = unreal.load_object(None, seq_path)
    if not seq:
        print(f"ERROR: Could not load Level Sequence {seq_path}")
        return
        
    settings = unreal.MovieSceneSequencePlaybackSettings()
    player, seq_actor = unreal.LevelSequencePlayer.create_level_sequence_player(world, seq, settings)
    if not player:
        print("ERROR: Failed to create Level Sequence Player")
        return
        
    print(f"Created Player: {player.get_name()}")
    
    bindings = seq.get_bindings()
    for binding in bindings:
        name = binding.get_name()
        guid = binding.get_id()
        binding_id = unreal.MovieSceneObjectBindingID()
        binding_id.set_editor_property("guid", guid)
        bound_objects = player.get_bound_objects(binding_id)
        print(f"Binding Class: {binding.get_possessed_object_class().get_name() if binding.get_possessed_object_class() else 'None'} | Name: {name} | GUID: {guid}")
        print(f"  Bound Objects count: {len(bound_objects)}")
        for obj in bound_objects:
            print(f"    - {obj.get_name()} (Class: {obj.get_class().get_name()})")

if __name__ == "__main__":
    run()
