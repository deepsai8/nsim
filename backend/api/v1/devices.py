# backend/api/v1/devices.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

router = APIRouter()

# Global variables: the single Unity WebSocket connection and a simple state store.
unity_ws = None
device_states = {
    "lamp": False,
    "tv": False,
    "radio": False,
    "kitchenlight": False,
}

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
            # If Unity sends back status updates in the format "device:status:on" or "device:status:off",
            # update our state store.
            parts = data.split(":")
            if len(parts) == 3 and parts[1] == "status":
                device = parts[0].lower()
                device_states[device] = (parts[2].lower() == "on")
    except WebSocketDisconnect:
        print("Unity disconnected")
        unity_ws = None

# -----------------------------------------------------------
# Lamp Endpoints
# -----------------------------------------------------------
@router.post("/lamp")
async def toggle_lamp(command: DeviceCommand):
    global unity_ws, device_states
    if unity_ws is None:
        return {"error": "Unity client not connected"}
    desired_state = command.state.lower()
    current_state = "on" if device_states.get("lamp", False) else "off"
    if current_state == desired_state:
        return {"message": f"Lamp is already {desired_state}."}
    message = f"lamp:{command.state}"
    await unity_ws.send_text(message)
    device_states["lamp"] = (desired_state == "on")
    return {"message": "Command sent", "command": message}

@router.get("/lamp/status")
async def get_lamp_status():
    return {"lamp": device_states["lamp"]}

# -----------------------------------------------------------
# TV Endpoints
# -----------------------------------------------------------
@router.post("/tv")
async def toggle_tv(command: DeviceCommand):
    global unity_ws, device_states
    if unity_ws is None:
        return {"error": "Unity client not connected"}
    desired_state = command.state.lower()
    current_state = "on" if device_states.get("tv", False) else "off"
    if current_state == desired_state:
        return {"message": f"TV is already {desired_state}."}
    message = f"tv:{command.state}"
    await unity_ws.send_text(message)
    device_states["tv"] = (desired_state == "on")
    return {"message": "Command sent", "command": message}

@router.get("/tv/status")
async def get_tv_status():
    return {"tv": device_states["tv"]}

# -----------------------------------------------------------
# Radio Endpoints
# -----------------------------------------------------------
@router.post("/radio")
async def toggle_radio(command: DeviceCommand):
    global unity_ws, device_states
    if unity_ws is None:
        return {"error": "Unity client not connected"}
    desired_state = command.state.lower()
    current_state = "on" if device_states.get("radio", False) else "off"
    if current_state == desired_state:
        return {"message": f"Radio is already {desired_state}."}
    message = f"radio:{command.state}"
    await unity_ws.send_text(message)
    device_states["radio"] = (desired_state == "on")
    return {"message": "Command sent", "command": message}

@router.get("/radio/status")
async def get_radio_status():
    return {"radio": device_states["radio"]}

# -----------------------------------------------------------
# Kitchen Wall Light Endpoints
# -----------------------------------------------------------
@router.post("/kitchenlight")
async def toggle_kitchen_light(command: DeviceCommand):
    global unity_ws, device_states
    if unity_ws is None:
        return {"error": "Unity client not connected"}
    desired_state = command.state.lower()
    current_state = "on" if device_states.get("kitchenlight", False) else "off"
    if current_state == desired_state:
        return {"message": f"Kitchen lights are already {desired_state}."}
    message = f"kitchenlight:{command.state}"
    await unity_ws.send_text(message)
    device_states["kitchenlight"] = (desired_state == "on")
    return {"message": "Command sent", "command": message}

@router.get("/kitchenlight/status")
async def get_kitchen_light_status():
    return {"kitchenlight": device_states["kitchenlight"]}
