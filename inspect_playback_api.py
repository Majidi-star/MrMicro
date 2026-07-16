import unreal

def run():
    print("---------------- SET_PLAYBACK_POSITION SIGNATURE ----------------")
    player_cls = unreal.LevelSequencePlayer
    method = player_cls.set_playback_position
    print("Docstring:")
    print(method.__doc__)
    
    # Also inspect any classes matching Playback
    print("\nPlayback matches in unreal:")
    for attr in dir(unreal):
        if "playback" in attr.lower():
            print(f"  {attr}")

if __name__ == "__main__":
    run()
