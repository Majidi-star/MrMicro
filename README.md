# MetaHuman Micro-Expression Training App

This repository contains an end-to-end stack for generating and evaluating micro-expression training flashcards. It uses an instance of Unreal Engine 5 to generate cinematic MetaHuman facial expressions via the Movie Render Queue, which are then passed to a high-fidelity React web application for user evaluation and testing.

## System Architecture

The application is split across three decoupled tiers:
1. **React Web Application (`webapp/`)**: The frontend UI where users practice identifying micro-expressions (Action Units and Fundamental Emotions). It includes a massive viewport overlay, an interactive comparison slider, and an intricate settings configuration panel.
2. **FastAPI Broker (`backend/main.py`)**: A lightweight Python ASGI server that acts as a bridge. It intercepts HTTP POST payloads from the React UI and proxies the execution orders into the running instance of Unreal Engine via a direct TCP Socket. 
3. **Unreal Engine TCP Executor (`backend/ue_mrp_client.py`)**: A Python script operating entirely *within* the Unreal Engine 5 Editor environment. It listens on an internal socket for render payloads, configures the `Face_ControlBoard_CtrlRig`, and spawns asynchronous Movie Render Queue (MRQ) jobs to generate images back into the web application's public assets folder.

---

## 🚀 How to Start the Program

Because this program bridges an active 3D rendering engine to a web server, you must launch the three components simultaneously to activate the loop. 

### Step 1: Launch the Backend Broker (FastAPI)
1. Open a terminal (PowerShell/Command Prompt) and navigate to the project directory:
   ```bash
   cd "C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\backend"
   ```
2. Start the FastAPI server using Uvicorn:
   ```bash
   uvicorn main:app --port 8123
   ```
   *Note: This terminal must remain open. You should see it state that it is listening for Unreal Engine connections on `127.0.0.1:8890`.*

### Step 2: Connect Unreal Engine
1. Launch **Unreal Engine 5** and open the `Metahuman.uproject` project.
2. Open the foundational Level Sequence and Map (ensure you are loaded into `final_level.umap`).
3. Open the **Output Log** panel inside Unreal Engine. At the bottom, change the command bar from `Cmd` to `Python`.
4. Run the TCP connection script. You can execute this by typing:
   ```python
   import sys
   import importlib
   # Append the backend directory so Unreal can find the scripts
   sys.path.append(r"C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\backend")
   
   import ue_mrp_client
   importlib.reload(ue_mrp_client)
   
   import mrq_batch_dataset
   importlib.reload(mrq_batch_dataset)
   
   server = ue_mrp_client.UEMRQServer()
   server.connect()
   ```
   *You should see a success log in Unreal and the FastAPI terminal stating "Unreal Engine connected!".*

### Step 3: Launch the Frontend Web App (React)
1. Open a *new* terminal and navigate to the web application directory:
   ```bash
   cd "C:\Users\Amirhosein\Documents\Unreal Projects\Metahuman\webapp"
   ```
2. Start the Vite development server:
   ```bash
   npm run dev
   ```
3. Open your browser and navigate to the local URL provided (usually `http://localhost:5173`).

---

## 📦 Generating Static Data Batches

If you want to generate a static dataset so you can decouple react and host this application online for free (without needing an active Unreal Engine GPU running 24/7), you should generate a pre-rendered Database. 

Here is EXACTLY what you need to do to generate a batch:
1. **Ensure the Stack is Online:** Ensure you have completed Steps 1 through 3 above. FastAPI must be running on Port 8123, the React App on Port 5173, and Unreal Engine must be connected (`ue_mrp_client.py` executing inside the Editor).
2. **Prepare Unreal Editor:** Verify that Unreal Engine is resting inside `final_level.umap`. 
3. **Open Settings:** Go into your browser to `http://localhost:5173` and click the Settings (`⚙️`) icon in the top-right corner.
4. **Configure Database Constraints:** Navigate to the `🗄️ Database` tab.
5. **Set Batch Size:** Select your Batch Target (e.g., *Micro-Test (5)* to quickly verify the pipeline).
6. **Trigger Batch:** Click **COMMENCE UNREAL BATCH GENERATION**.
7. **Observe Automation:** The Unreal Engine Editor will violently lock up and take control as the Movie Render Queue algorithm spawns executor jobs. *Do not interact with the engine during this phase to avoid crashing the render.*
8. **Finalization:** Once finished, a structured `database.json` file alongside all the exported cinematic PNGs will be instantly saved to `webapp/public/dataset/`!
