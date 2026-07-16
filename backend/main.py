import os
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import uuid

# To run: uvicorn main:app --reload --port 8000

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manage Unreal Engine socket connections
ue_clients = []
active_requests = {}

async def handle_ue_client(reader, writer):
    print("Unreal Engine connected!")
    ue_clients.append(writer)
    try:
        while True:
            data = await reader.read(4096)
            if not data:
                break
            message = data.decode().strip()
            print(f"Received from UE: {message}")
            try:
                response = json.loads(message)
                task_id = response.get("task_id")
                if task_id in active_requests:
                    active_requests[task_id].set_result(response)
            except json.JSONDecodeError as e:
                print(f"Error parsing UE response: {e}")
    except Exception as e:
        print(f"UE connection error: {e}")
    finally:
        print("Unreal Engine disconnected!")
        if writer in ue_clients:
            ue_clients.remove(writer)
        writer.close()

async def start_socket_server():
    server = await asyncio.start_server(handle_ue_client, '127.0.0.1', 8890)
    print("FastAPI internal TCP server listening on 127.0.0.1:8890 for Unreal Engine")
    async with server:
        await server.serve_forever()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_socket_server())

@app.get("/")
def health_check():
    return {"status": "ok", "ue_connected": len(ue_clients) > 0}

@app.post("/api/render")
async def render_image(payload: dict):
    """
    Called by the React WebApp.
    Payload shape: {"emotion": "ANGER", "intensity": 75, "aus": ["AU4", "AU5"]}
    """
    if not ue_clients:
        raise HTTPException(status_code=503, detail="Unreal Engine is not connected to the socket server")
    
    task_id = str(uuid.uuid4())
    payload["task_id"] = task_id
    
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    active_requests[task_id] = future
    
    # Send JSON order to Unreal
    writer = ue_clients[0]
    out_cmd = json.dumps(payload) + "\n"
    writer.write(out_cmd.encode())
    await writer.drain()
    print(f"Sent task {task_id} to UE.")
    
    # Wait for the UE client to process and return the result
    try:
        # Wait up to 120 seconds during heavy Movie Render Queue generation
        result = await asyncio.wait_for(future, timeout=120.0)
        return result
    except asyncio.TimeoutError:
        del active_requests[task_id]
        raise HTTPException(status_code=504, detail="Timeout waiting for Unreal Engine render")

@app.post("/api/generate_batch")
async def generate_batch(payload: dict):
    """
    Called by the React WebApp to lock UE into a bulk generation setup.
    Payload shape: {"num_images": 50, "intensity_mode": "Maximum", "quality": "4K"}
    """
    if not ue_clients:
        raise HTTPException(status_code=503, detail="Unreal Engine is not connected to the socket server")
    
    task_id = str(uuid.uuid4())
    payload["task_id"] = task_id
    payload["command"] = "generate_batch"
    
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    active_requests[task_id] = future
    
    # Send JSON batch order to Unreal
    writer = ue_clients[0]
    out_cmd = json.dumps(payload) + "\n"
    writer.write(out_cmd.encode())
    await writer.drain()
    print(f"Sent BATCH task {task_id} to UE.")
    
    try:
        # A batch job might take quite a long time depending on num_images
        result = await asyncio.wait_for(future, timeout=3600.0) # wait up to 1 hr
        return result
    except asyncio.TimeoutError:
        del active_requests[task_id]
        raise HTTPException(status_code=504, detail="Timeout wait exhausted for Batch generation")

@app.get("/api/batch_progress")
async def batch_progress():
    progress_file = r"C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\backend\progress.json"
    if os.path.exists(progress_file):
        try:
            with open(progress_file, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"status": "idle"}

@app.post("/api/cancel_batch")
async def cancel_batch():
    with open(r"C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\backend\cancel_flag.txt", "w") as f:
        f.write("CANCEL")
    return {"status": "cancelled"}
