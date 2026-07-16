import os
import json
import random
try:
    import unreal
except ImportError:
    pass

def apply_emotion_to_sequence_asset(sequence_path, emotion, intensity):
    seq = unreal.load_object(None, sequence_path)
    if not seq:
        unreal.log_error(f"Failed to load sequence {sequence_path}")
        return []

    cr_section = None
    for binding in seq.get_bindings():
        for t in binding.get_tracks():
            if isinstance(t, unreal.MovieSceneControlRigParameterTrack):
                for sec in t.get_sections():
                    if isinstance(sec, unreal.MovieSceneControlRigParameterSection):
                        cr_section = sec
                        break

    if not cr_section:
        unreal.log_error("Control Rig Parameter Section not found in sequence!")
        return []

    try:
        import json
        with open(r"C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\face_controlboard_controls.json", "r") as f:
            all_ctrls = json.load(f)
        all_controls = [c["name"] for c in all_ctrls if c.get("type", "").upper() == "FLOAT"]
    except Exception as e:
        unreal.log_warning(f"Could not load face controls JSON for full reset: {e}")
        all_controls = [
            "CTRL_L_mouth_cornerPull", "CTRL_R_mouth_cornerPull",
            "CTRL_L_brow_down", "CTRL_R_brow_down", "CTRL_C_mouth_stretch",
            "CTRL_L_brow_up", "CTRL_R_brow_up",
            "CTRL_L_mouth_cornerDepress", "CTRL_R_mouth_cornerDepress",
            "CTRL_L_mouth_stretch", "CTRL_R_mouth_stretch",
            "CTRL_L_nose_wrinkle", "CTRL_R_nose_wrinkle",
            "CTRL_L_mouth_dimple"
        ]
    time = unreal.FrameNumber(0)
    for c in all_controls:
        cr_section.add_scalar_parameter_key(unreal.Name(c), time, 0.0)

    mapping = {
        "HAPPINESS": [("CTRL_L_mouth_cornerPull", 1.0), ("CTRL_R_mouth_cornerPull", 1.0)],
        "ANGER": [("CTRL_L_brow_down", 1.0), ("CTRL_R_brow_down", 1.0)],
        "SURPRISE": [("CTRL_L_brow_raiseIn", 1.0), ("CTRL_R_brow_raiseIn", 1.0), ("CTRL_L_brow_raiseOut", 1.0), ("CTRL_R_brow_raiseOut", 1.0), ("CTRL_C_jaw_openExtreme", 0.5)], 
        "SADNESS": [("CTRL_L_mouth_cornerDepress", 1.0), ("CTRL_R_mouth_cornerDepress", 1.0), ("CTRL_L_brow_raiseIn", 1.0), ("CTRL_R_brow_raiseIn", 1.0)],
        "FEAR": [("CTRL_L_brow_raiseIn", 1.0), ("CTRL_R_brow_raiseIn", 1.0), ("CTRL_L_mouth_stretch", 1.0), ("CTRL_R_mouth_stretch", 1.0)],
        "DISGUST": [("CTRL_L_nose_wrinkleUpper", 1.0), ("CTRL_R_nose_wrinkleUpper", 1.0), ("CTRL_L_mouth_upperLipRaise", 1.0), ("CTRL_R_mouth_upperLipRaise", 1.0)],
        "CONTEMPT": [("CTRL_L_mouth_cornerPull", 1.0), ("CTRL_L_mouth_dimple", 1.0)]
    }
    
    controls = mapping.get(emotion, [])
    scaled_controls = [(c[0], c[1] * intensity) for c in controls]
    
    for c, val in scaled_controls:
        cr_section.add_scalar_parameter_key(unreal.Name(c), time, val)
        
    return scaled_controls

class AutomatedBatchGenerator:
    def __init__(self, config):
        self.num_images = config.get("num_images", 5)
        self.quality = config.get("quality", "1080p")
        self.intensity_min = config.get("intensity_min", 0.1)
        self.intensity_max = config.get("intensity_max", 1.0)
        
        self.emotions = ["ANGER", "CONTEMPT", "DISGUST", "FEAR", "HAPPINESS", "SADNESS", "SURPRISE"]
        
        # Load weights for custom probability distribution
        weights_config = config.get("emotion_weights", {})
        self.emotion_weights = []
        for emo in self.emotions:
            self.emotion_weights.append(float(weights_config.get(emo, 10.0)))
            
        total_weight = sum(self.emotion_weights)
        if total_weight <= 0:
            self.emotion_weights = [1.0] * len(self.emotions)
        
        self.current_iteration = 0
        self.database = []
        
        self.sequence_path = "/Game/micro_expression"
        self.map_path = "/Game/final_level"
        self.output_dir = "C:/Users/Amirhosein/Documents/Unreal Projects/Metahuman/webapp/public/dataset"
        
        self.active_executor = None
        self.on_complete_callback = None

    def start(self):
        import os, time, json
        unreal.log("Starting Automated Batch Generation...")
        self.start_time = time.time()
        
        db_path = os.path.join(self.output_dir, "database.json")
        if os.path.exists(db_path):
            try:
                with open(db_path, "r") as f:
                    self.database = json.load(f)
            except Exception as e:
                pass

        try:
            if os.path.exists(r"C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\backend\progress.json"):
                os.remove(r"C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\backend\progress.json")
            if os.path.exists(r"C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\backend\cancel_flag.txt"):
                os.remove(r"C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\backend\cancel_flag.txt")
        except: pass

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.run_next_iteration()

    def get_intensity_value(self):
        import random
        return random.uniform(self.intensity_min, self.intensity_max)

    def run_next_iteration(self):
        import os, json, time
        
        if os.path.exists(r"C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\backend\cancel_flag.txt"):
            unreal.log_warning("User cancelled batch generation.")
            try: os.remove(r"C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\backend\cancel_flag.txt")
            except: pass
            self.finalize_batch()
            return
            
        if self.current_iteration >= self.num_images:
            self.finalize_batch()
            return
            
        is_neutral = (self.current_iteration == 0)
        
        emotion = "NEUTRAL" if is_neutral else random.choices(self.emotions, weights=self.emotion_weights)[0]
        intensity = 0.0 if is_neutral else self.get_intensity_value()
        
        unreal.log(f"Iteration {self.current_iteration+1}/{self.num_images}: Rendering {emotion} at {intensity}")
        
        # 0. Write analytics progress
        elapsed = time.time() - getattr(self, "start_time", time.time())
        avg = elapsed / max(1, self.current_iteration)
        eta_seconds = (self.num_images - self.current_iteration) * avg
        try:
            with open(r"C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\backend\progress.json", "w") as f:
                json.dump({"status": "generating", "current": self.current_iteration, "total": self.num_images, "elapsed": elapsed, "eta": eta_seconds}, f)
        except: pass
        
        # 1. Inject Control Keys
        injected_controls = apply_emotion_to_sequence_asset(self.sequence_path, emotion, intensity)
        
        # 2. Setup MRQ
        subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
        queue = subsystem.get_queue()
        queue.delete_all_jobs()

        global_id = len(self.database)

        job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
        job.job_name = f"Flashcard_{global_id:04d}_{emotion}"
        job.map = unreal.SoftObjectPath(f"{self.map_path}.{self.map_path.split('/')[-1]}")
        job.sequence = unreal.SoftObjectPath(f"{self.sequence_path}.{self.sequence_path.split('/')[-1]}")

        config = job.get_configuration()
        for setting in config.get_all_settings(): config.remove_setting(setting)
        
        # Resolution mapping
        res = (1080, 1440)
        if self.quality == "720p": res = (720, 960)
        elif self.quality == "4K": res = (2160, 2880)

        output_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
        output_setting.output_directory = unreal.DirectoryPath(self.output_dir)
        output_setting.file_name_format = "{job_name}{frame_number}"
        output_setting.output_resolution = unreal.IntPoint(res[0], res[1])
        
        config.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
        config.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
        output_setting.use_custom_playback_range = True
        output_setting.custom_start_frame = 0
        output_setting.custom_end_frame = 1

        self.current_job_metadata = {
            "image": f"{job.job_name}0000.png", # MRQ appends frame 0000 automatically
            "emotions": [emotion] if not is_neutral else [],
            "intensity": intensity,
            "controls_applied": dict(injected_controls)
        }

        # 3. Execute MRQ
        self.active_executor = unreal.MoviePipelinePIEExecutor()
        self.active_executor.on_executor_finished_delegate.add_callable(self.on_mrq_finished)
        subsystem.render_queue_with_executor_instance(self.active_executor)

    def on_mrq_finished(self, executor, success):
        unreal.log(f"Render Success: {success}")
        
        if success:
            self.database.append(self.current_job_metadata)

        self.active_executor = None
        self.current_iteration += 1
        
        # Schedule the next iteration on the next tick to clear the async queue bounds
        self.tick_handle = unreal.register_slate_post_tick_callback(self.tick_trigger_next)

    def tick_trigger_next(self, delta):
        # We unregister immediately so it only fires once
        if hasattr(self, 'tick_handle'):
            unreal.unregister_slate_post_tick_callback(self.tick_handle)
            del self.tick_handle
            
        self.run_next_iteration()

    def finalize_batch(self):
        db_path = os.path.join(self.output_dir, "database.json")
        try:
            with open(db_path, "w") as f:
                json.dump(self.database, f, indent=4)
            unreal.log(f"Batch Dataset Generated Successfully! Wrote {len(self.database)} records to {db_path}")
            if self.on_complete_callback:
                self.on_complete_callback(db_path)
        except Exception as e:
            unreal.log_error(f"Failed to write database.json: {e}")
