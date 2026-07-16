import unreal
import json
import os

def run():
    asset_path = "/Game/MetaHumans/Common/Face/Face_ControlBoard_CtrlRig.Face_ControlBoard_CtrlRig"
    print(f"Loading asset: {asset_path}")
    rig_blueprint = unreal.load_object(None, asset_path)
    
    if not rig_blueprint:
        print("Retrying load with short path...")
        rig_blueprint = unreal.load_object(None, "/Game/MetaHumans/Common/Face/Face_ControlBoard_CtrlRig")
        
    if not rig_blueprint:
        print("ERROR: Could not load Face_ControlBoard_CtrlRig blueprint")
        return
        
    hierarchy = rig_blueprint.hierarchy
    all_keys = hierarchy.get_all_keys()
    
    controls = []
    for key in all_keys:
        if key.type == unreal.RigElementType.CONTROL:
            control_name = str(key.name)
            value_type = "Unknown"
            
            try:
                if hierarchy.contains(key):
                    # Use modern, non-deprecated API
                    settings = hierarchy.get_control_settings(key)
                    val_type = settings.control_type
                    value_type = val_type.name if hasattr(val_type, "name") else str(val_type)
            except Exception as e:
                value_type = f"Error: {str(e)}"
                
            controls.append({
                "name": control_name,
                "type": value_type
            })
            
    # Alphabetically sort the controls by name for convenience
    controls.sort(key=lambda x: x["name"])
    
    output_path = r"c:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\face_controlboard_controls.json"
    with open(output_path, "w") as f:
        json.dump(controls, f, indent=4)
        
    print(f"SUCCESS: Exported {len(controls)} controls to {output_path}")

if __name__ == "__main__":
    run()
