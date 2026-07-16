import unreal

def run():
    print("---------------- MOVIE SCENE PLAYBACK PARAMS ----------------")
    params_cls = unreal.MovieSceneSequencePlaybackParams
    print("Init doc:")
    print(params_cls.__doc__)
    print("\nProperties:")
    for prop in params_cls.static_class().get_property_names():
        print(f"  {prop}")

if __name__ == "__main__":
    run()
