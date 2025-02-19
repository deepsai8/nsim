# backend/api/v1/devices.py
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

router = APIRouter()

# Check the flag: use Redis if the environment variable USE_REDIS is set to true.
USE_REDIS = os.getenv("USE_REDIS", "false").lower() in ("true", "1", "yes")

if USE_REDIS:
    import redis
    # Create a Redis client. decode_responses=True ensures we work with strings.
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    print("Using Redis for device state.")
else:
    # In-memory fallback for device states.
    device_states = {
        "lamp": True,
        "tv": False,
        "radio": False,
        "kitchenlight": True,
    }
    print("Using in-memory device state storage.")

# Helper functions to get and set device status.
def get_device_status(device: str) -> str:
    if USE_REDIS:
        return r.get(device) or "off"
    else:
        return device_states.get(device, "off")

def set_device_status(device: str, state: str):
    if USE_REDIS:
        r.set(device, state)
    else:
        device_states[device] = state

# Global variable for the Unity WebSocket connection.
unity_ws = None

class DeviceCommand(BaseModel):
    state: str  # Expected values: "on" or "off"

# -----------------------------------------------------------
# WebSocket Endpoint
# -----------------------------------------------------------
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global unity_ws
    await websocket.accept()
    unity_ws = websocket
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received from Unity: {data}")
            # Expected format: "device:status:on" or "device:status:off"
            parts = data.split(":")
            if len(parts) == 3 and parts[1] == "status":
                device = parts[0].lower()
                state = parts[2].lower()  # "on" or "off"
                set_device_status(device, state)
    except WebSocketDisconnect:
        print("Unity disconnected")
        unity_ws = None

# -----------------------------------------------------------
# Lamp Endpoints
# -----------------------------------------------------------
@router.post("/lamp")
async def toggle_lamp(command: DeviceCommand):
    global unity_ws
    if unity_ws is None:
        return {"error": "Unity client not connected"}
    desired_state = command.state.lower()
    current_state = get_device_status("lamp")
    if current_state == desired_state:
        return {"message": f"Lamp is already {desired_state}."}
    message = f"lamp:{command.state}"
    await unity_ws.send_text(message)
    set_device_status("lamp", desired_state)
    return {"message": "Command sent", "command": message}

@router.get("/lamp/status")
async def get_lamp_status():
    state = get_device_status("lamp")
    return {"lamp": state == "on"}

# -----------------------------------------------------------
# TV Endpoints
# -----------------------------------------------------------
@router.post("/tv")
async def toggle_tv(command: DeviceCommand):
    global unity_ws
    if unity_ws is None:
        return {"error": "Unity client not connected"}
    desired_state = command.state.lower()
    current_state = get_device_status("tv")
    if current_state == desired_state:
        return {"message": f"TV is already {desired_state}."}
    message = f"tv:{command.state}"
    await unity_ws.send_text(message)
    set_device_status("tv", desired_state)
    return {"message": "Command sent", "command": message}

@router.get("/tv/status")
async def get_tv_status():
    state = get_device_status("tv")
    return {"tv": state == "on"}

# -----------------------------------------------------------
# Radio Endpoints
# -----------------------------------------------------------
@router.post("/radio")
async def toggle_radio(command: DeviceCommand):
    global unity_ws
    if unity_ws is None:
        return {"error": "Unity client not connected"}
    desired_state = command.state.lower()
    current_state = get_device_status("radio")
    if current_state == desired_state:
        return {"message": f"Radio is already {desired_state}."}
    message = f"radio:{command.state}"
    await unity_ws.send_text(message)
    set_device_status("radio", desired_state)
    return {"message": "Command sent", "command": message}

@router.get("/radio/status")
async def get_radio_status():
    state = get_device_status("radio")
    return {"radio": state == "on"}

# -----------------------------------------------------------
# Kitchen Wall Light Endpoints
# -----------------------------------------------------------
@router.post("/kitchenlight")
async def toggle_kitchen_light(command: DeviceCommand):
    global unity_ws
    if unity_ws is None:
        return {"error": "Unity client not connected"}
    desired_state = command.state.lower()
    current_state = get_device_status("kitchenlight")
    if current_state == desired_state:
        return {"message": f"Kitchen lights are already {desired_state}."}
    message = f"kitchenlight:{command.state}"
    await unity_ws.send_text(message)
    set_device_status("kitchenlight", desired_state)
    return {"message": "Command sent", "command": message}

@router.get("/kitchenlight/status")
async def get_kitchen_light_status():
    state = get_device_status("kitchenlight")
    return {"kitchenlight": state == "on"}
