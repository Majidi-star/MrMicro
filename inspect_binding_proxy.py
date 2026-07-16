import unreal

def run():
    print("---------------- MOVIE SCENE BINDINGS / ID INSPECTION ----------------")
    
    # 1. MovieSceneBindingProxy methods
    print("MovieSceneBindingProxy methods:")
    proxy_cls = unreal.MovieSceneBindingProxy
    print(dir(proxy_cls))
    
    # 2. MovieSceneObjectBindingID properties and methods
    print("\nMovieSceneObjectBindingID:")
    id_cls = unreal.MovieSceneObjectBindingID
    print(dir(id_cls))
    print(id_cls.__doc__)
    # Trace properties
    try:
        for prop in id_cls.static_class().get_property_names():
            print(f"  {prop}")
    except Exception as e:
        print(f"  Cannot use static_class: {e}")

if __name__ == "__main__":
    run()
