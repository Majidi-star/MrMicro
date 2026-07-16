import unreal

def run():
    print(help(unreal.AnimInstance.get_active_curve_names))
    # Also check if get_all_curve_names requires arguments
    print(help(unreal.AnimInstance.get_all_curve_names))

if __name__ == "__main__":
    run()
