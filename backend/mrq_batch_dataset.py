import os
import json
import random
try:
    import unreal
except ImportError:
    pass

import math

def ease_in_out_cubic(t):
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - math.pow(-2 * t + 2, 3) / 2

def apply_emotion_to_sequence_asset(sequence_path, emotion, intensity, video_timings=None):
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

    # Clear keys
    try:
        channels = cr_section.get_all_channels()
        for chan in channels:
            keys = chan.get_keys()
            for k in keys:
                try: chan.remove_key(k)
                except: pass
    except Exception as e:
        pass

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

    # Initialize all controls to 0.0 at frame 0 to prevent cross-contamination from previous renders
    time_zero = unreal.FrameNumber(0)
    for c in all_controls:
        cr_section.add_scalar_parameter_key(unreal.Name(c), time_zero, 0.0)

    # Load Expression Profile
    try:
        with open(r"C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\backend\expression_profiles.json", "r") as f:
            profiles = json.load(f)
    except:
        profiles = {}
        
    profile = profiles.get(emotion, {})
    if not profile and emotion != "NEUTRAL":
        # Fallback to simple defaults
        fallback_map = {
            "HAPPINESS": ["CTRL_L_mouth_cornerPull", "CTRL_R_mouth_cornerPull"],
            "ANGER": ["CTRL_L_brow_down", "CTRL_R_brow_down"],
            "SURPRISE": ["CTRL_L_brow_raiseIn", "CTRL_R_brow_raiseIn", "CTRL_L_brow_raiseOut", "CTRL_R_brow_raiseOut"], 
            "SADNESS": ["CTRL_L_mouth_cornerDepress", "CTRL_R_mouth_cornerDepress", "CTRL_L_brow_raiseIn", "CTRL_R_brow_raiseIn"],
            "FEAR": ["CTRL_L_brow_raiseIn", "CTRL_R_brow_raiseIn", "CTRL_L_mouth_stretch", "CTRL_R_mouth_stretch"],
            "DISGUST": ["CTRL_L_nose_wrinkleUpper", "CTRL_R_nose_wrinkleUpper", "CTRL_L_mouth_upperLipRaise", "CTRL_R_mouth_upperLipRaise"],
            "CONTEMPT": ["CTRL_L_mouth_cornerPull", "CTRL_L_mouth_dimple"]
        }
        for c in fallback_map.get(emotion, []):
            profile[c] = {"target": 1.0, "delay_ms": 0, "easing": "linear", "jitter": 0.0}

    scaled_controls = []
    
    if video_timings:
        tick_res = seq.get_tick_resolution()
        display_rate = seq.get_display_rate()
        ticks_per_frame = int(tick_res.numerator / display_rate.numerator)
        fps = video_timings["fps"]
        
        n_total = video_timings["n_total"]
        t_neutral_start = video_timings["n_neutral_start"] / fps
        t_onset_dur = (video_timings["n_onset"] - video_timings["n_neutral_start"]) / fps
        t_hold_dur = (video_timings["n_hold"] - video_timings["n_onset"]) / fps
        t_offset_dur = (video_timings["n_offset"] - video_timings["n_hold"]) / fps
        
        # Bake every frame
        for frame_idx in range(n_total + 1):
            time_sec = frame_idx / fps
            tick = frame_idx * ticks_per_frame
            
            # Apply profile controls
            for c_name, params in profile.items():
                target_val = params.get("target", 1.0) * intensity
                delay = params.get("delay_ms", 0) / 1000.0
                easing = params.get("easing", "linear")
                jitter_amp = params.get("jitter", 0.0)
                
                # Shift timings by delay
                start_onset = t_neutral_start + delay
                end_onset = start_onset + t_onset_dur
                start_offset = video_timings["n_hold"] / fps + delay
                end_offset = start_offset + t_offset_dur
                
                current_val = 0.0
                if time_sec < start_onset:
                    current_val = 0.0
                elif time_sec < end_onset:
                    progress = (time_sec - start_onset) / t_onset_dur
                    if easing == "cubic": progress = ease_in_out_cubic(progress)
                    current_val = progress * target_val
                elif time_sec < start_offset:
                    current_val = target_val
                    # Apply Jitter
                    if jitter_amp > 0:
                        current_val += math.sin(time_sec * 30.0) * jitter_amp * intensity
                elif time_sec < end_offset:
                    progress = (time_sec - start_offset) / t_offset_dur
                    if easing == "cubic": progress = ease_in_out_cubic(progress)
                    current_val = target_val - (progress * target_val)
                else:
                    current_val = 0.0
                    
                cr_section.add_scalar_parameter_key(unreal.Name(c_name), unreal.FrameNumber(tick), current_val)
                
                if frame_idx == 0:
                    scaled_controls.append((c_name, target_val))
                    
    else:
        # Static case: apply intensity on frame 0
        time_zero = unreal.FrameNumber(0)
        for c_name, params in profile.items():
            val = params.get("target", 1.0) * intensity
            cr_section.add_scalar_parameter_key(unreal.Name(c_name), time_zero, val)
            scaled_controls.append((c_name, val))
            
    return scaled_controls

class AutomatedBatchGenerator:
    def __init__(self, config):
        self.num_images = config.get("num_images", 5)
        self.quality = config.get("quality", "1080p")
        self.intensity_min = config.get("intensity_min", 0.1)
        self.intensity_max = config.get("intensity_max", 1.0)
        
        # New video dataset configurations
        self.is_video = (config.get("type") in ["video", "videos"])
        self.hold_duration_ms = int(config.get("hold_duration_ms", 100))
        
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

    def calculate_video_timings(self, hold_duration_ms):
        # Determine optimal frame rate based on expression duration
        if hold_duration_ms <= 100:
            fps = 120
        elif hold_duration_ms <= 250:
            fps = 60
        else:
            fps = 30
            
        # Timings in seconds
        t_neutral_start = 0.2
        t_onset = 0.08
        t_hold = hold_duration_ms / 1000.0
        t_offset = 0.12
        t_neutral_end = 0.2
        
        # Frames
        n_neutral_start = int(round(t_neutral_start * fps))
        n_onset = n_neutral_start + int(round(t_onset * fps))
        n_hold = n_onset + int(round(t_hold * fps))
        n_offset = n_hold + int(round(t_offset * fps))
        n_total = n_offset + int(round(t_neutral_end * fps))
        
        return {
            "fps": fps,
            "n_neutral_start": n_neutral_start,
            "n_onset": n_onset,
            "n_hold": n_hold,
            "n_offset": n_offset,
            "n_total": n_total
        }

    def start(self):
        import os, time, json
        db_filename = "database_video.json" if self.is_video else "database.json"
        unreal.log(f"Starting Automated Batch Generation ({'Video' if self.is_video else 'Flashcard'})...")
        self.start_time = time.time()
        
        db_path = os.path.join(self.output_dir, db_filename)
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
        
        # Write progress status
        elapsed = time.time() - getattr(self, "start_time", time.time())
        avg = elapsed / max(1, self.current_iteration)
        eta_seconds = (self.num_images - self.current_iteration) * avg
        try:
            with open(r"C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\backend\progress.json", "w") as f:
                json.dump({"status": "generating", "current": self.current_iteration, "total": self.num_images, "elapsed": elapsed, "eta": eta_seconds}, f)
        except: pass
        
        # Load Level Sequence Object
        seq = unreal.load_object(None, self.sequence_path)
        global_id = len(self.database)
        
        # Setup Render Range & Timing
        if self.is_video:
            timings = self.calculate_video_timings(self.hold_duration_ms)
            
            # Configure sequence display rate and playback range
            seq.set_display_rate(unreal.FrameRate(numerator=timings["fps"], denominator=1))
            seq.set_playback_start(0)
            seq.set_playback_end(timings["n_total"] - 1)
            
            # Inject animated keys into the Control Rig section
            injected_controls = apply_emotion_to_sequence_asset(self.sequence_path, emotion, intensity, timings)
            n_total = timings["n_total"]
            start_frame = 0
            end_frame = n_total
            job_name_val = f"Video_{global_id:04d}_{emotion}"
        else:
            # Static Flashcard Mode:
            # Reset display rate to standard 30fps and render frame 0
            seq.set_display_rate(unreal.FrameRate(numerator=30, denominator=1))
            seq.set_playback_start(0)
            seq.set_playback_end(0)
            
            injected_controls = apply_emotion_to_sequence_asset(self.sequence_path, emotion, intensity, None)
            start_frame = 0
            end_frame = 1
            job_name_val = f"Flashcard_{global_id:04d}_{emotion}"
        
        # Setup Movie Render Queue
        subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
        queue = subsystem.get_queue()
        queue.delete_all_jobs()

        job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
        job.job_name = job_name_val
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
        output_setting.file_name_format = "{job_name}" if self.is_video else "{job_name}{frame_number}"
        output_setting.output_resolution = unreal.IntPoint(res[0], res[1])
        
        config.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
        if self.is_video:
            config.find_or_add_setting_by_class(unreal.MoviePipelineMP4EncoderOutput)
        else:
            config.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
            
        output_setting.use_custom_playback_range = True
        output_setting.custom_start_frame = start_frame
        output_setting.custom_end_frame = end_frame

        if self.is_video:
            self.current_job_metadata = {
                "id": f"Video_{global_id:04d}_{emotion}",
                "emotions": [emotion] if not is_neutral else [],
                "intensity": intensity,
                "controls_applied": dict(injected_controls),
                "duration_ms": self.hold_duration_ms,
                "fps": timings["fps"],
                "total_frames": n_total,
                "video_url": f"{job.job_name}.mp4"
            }
        else:
            self.current_job_metadata = {
                "image": f"{job.job_name}0000.png",
                "emotions": [emotion] if not is_neutral else [],
                "intensity": intensity,
                "controls_applied": dict(injected_controls)
            }

        # Execute MRQ
        self.active_executor = unreal.MoviePipelinePIEExecutor()
        self.active_executor.on_executor_finished_delegate.add_callable(self.on_mrq_finished)
        subsystem.render_queue_with_executor_instance(self.active_executor)

    def on_mrq_finished(self, executor, success):
        unreal.log(f"Render Success: {success}")
        
        if success:
            self.database.append(self.current_job_metadata)

        self.active_executor = None
        self.current_iteration += 1
        
        # Schedule the next iteration on the next tick
        self.tick_handle = unreal.register_slate_post_tick_callback(self.tick_trigger_next)

    def tick_trigger_next(self, delta):
        if hasattr(self, 'tick_handle'):
            unreal.unregister_slate_post_tick_callback(self.tick_handle)
            del self.tick_handle
            
        self.run_next_iteration()

    def finalize_batch(self):
        db_filename = "database_video.json" if self.is_video else "database.json"
        db_path = os.path.join(self.output_dir, db_filename)
        try:
            with open(db_path, "w") as f:
                json.dump(self.database, f, indent=4)
            unreal.log(f"Batch Dataset Generated Successfully! Wrote {len(self.database)} records to {db_path}")
            if self.on_complete_callback:
                self.on_complete_callback(db_path)
        except Exception as e:
            unreal.log_error(f"Failed to write {db_filename}: {e}")
