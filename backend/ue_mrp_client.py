import socket
import json
import threading
import time

try:
    import unreal
except ImportError:
    # Dummy mock
    pass

class UEMRQServer:
    def __init__(self, host='127.0.0.1', port=8890):
        self.host = host
        self.port = port
        self.sock = None
        self.running = False
        self.task_queue = []
        self.tick_handle = None
        self.active_executor = None
        self.active_task_id = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.running = True
            
            t = threading.Thread(target=self.listen_loop)
            t.daemon = True
            t.start()
            
            self.tick_handle = unreal.register_slate_post_tick_callback(self.tick)
            unreal.log(f"Connected to FastAPI MRQ server at {self.host}:{self.port}!")
        except Exception as e:
            unreal.log_warning(f"Failed to connect to FastAPI: {e}")

    def disconnect(self):
        self.running = False
        if self.sock: self.sock.close()
        if self.tick_handle: unreal.unregister_slate_post_tick_callback(self.tick_handle)

    def listen_loop(self):
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(4096)
                if not data: break
                buffer += data.decode()
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        self.task_queue.append(json.loads(line))
            except Exception:
                break
        self.running = False

    def tick(self, delta_time):
        if len(self.task_queue) > 0 and self.active_executor is None:
            task = self.task_queue.pop(0)
            self.process_task(task)

    def process_task(self, task):
        if task.get("command") == "generate_batch":
            unreal.log("Intercepted Batch Generation Command!")
            import mrq_batch_dataset
            import importlib
            importlib.reload(mrq_batch_dataset)
            
            gen = mrq_batch_dataset.AutomatedBatchGenerator(task)
            def on_complete(db_path):
                self.send_response({"task_id": task.get("task_id"), "status": "success", "db": db_path})
            
            gen.on_complete_callback = on_complete
            gen.start()
            return

        unreal.log(f"Processing MRQ Task: {task}")
        self.active_task_id = task.get("task_id")
        emotion = task.get("emotion")
        
        # UI slider is 1-10. Scale to 0.1 - 1.0
        intensity = float(task.get("intensity", 10)) / 10.0

        sequence_path = "/Game/micro_expression"
        map_path = "/Game/final_level"
        output_dir = "C:/Users/Amirhosein/Documents/Unreal Projects/Metahuman/webapp/public/renders"

        # 1. Update Sequence (Physically forcing scalar parameter keys onto the track)
        try:
            import mrq_batch_dataset
            mrq_batch_dataset.apply_emotion_to_sequence_asset(sequence_path, emotion, intensity)
        except Exception as e:
            unreal.log_error(f"Failed to inject scalar parameters into sequence: {e}")

        # 2. Setup MRQ
        subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
        queue = subsystem.get_queue()
        queue.delete_all_jobs()

        job = queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
        job.job_name = f"Render_{self.active_task_id}"
        job.map = unreal.SoftObjectPath(f"{map_path}.{map_path.split('/')[-1]}")
        job.sequence = unreal.SoftObjectPath(f"{sequence_path}.{sequence_path.split('/')[-1]}")

        config = job.get_configuration()
        # Ensure clean config
        for setting in config.get_all_settings(): config.remove_setting(setting)
        
        # Add output settings
        output_setting = config.find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)
        output_setting.output_directory = unreal.DirectoryPath(output_dir)
        output_setting.file_name_format = "{job_name}{frame_number}"
        output_setting.output_resolution = unreal.IntPoint(450, 600)  # Portrait UI fit
        
        # Add render passes
        config.find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)
        config.find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)
        output_setting.use_custom_playback_range = True
        output_setting.custom_start_frame = 0
        output_setting.custom_end_frame = 1

        # 3. Execute MRQ
        self.active_executor = unreal.MoviePipelinePIEExecutor()
        self.active_executor.on_executor_finished_delegate.add_callable(self.on_mrq_finished)
        subsystem.render_queue_with_executor_instance(self.active_executor)

    def on_mrq_finished(self, executor, success):
        unreal.log(f"MRQ Job Finished. Success: {success}")
        
        # We know the output file name formatting
        # Output directory + job_name + frame number (e.g. Render_1230000.png)
        filename = f"Render_{self.active_task_id}0000.png"
        # React will access via public URL -> /renders/filename.jpg
        
        response = {
            "task_id": self.active_task_id,
            "status": "success" if success else "failed",
            "image_url": f"/renders/{filename}"
        }
        self.send_response(response)
        
        self.active_executor = None
        self.active_task_id = None

    def send_response(self, response):
        try:
            self.sock.sendall((json.dumps(response) + "\n").encode())
        except Exception as e:
            unreal.log_warning(f"Failed to reply: {e}")

# To start server within UE Python console:
# server = UEMRQServer()
# server.connect()
