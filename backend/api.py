from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from backend.models import Rule, Alert
from backend.rule_manager import RuleManager
from backend.websocket_manager import ws_manager

# --- Initialize Application & Managers ---
app = FastAPI(title="AI Monitoring System API - Enterprise Edition")
rule_manager = RuleManager()

# Add CORS Middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for legacy polling
latest_alerts: List[Alert] = []

# --- Pydantic Models for Requests ---
class NLPPrompt(BaseModel):
    text: str

# --- REST Endpoints (Rules) ---

@app.get("/rules", response_model=List[Rule])
def get_rules():
    """Returns all active rules from the database."""
    return rule_manager.get_rules()

@app.post("/rules", response_model=Rule)
def create_rule(rule: Rule):
    """Manually creates a new rule (Used by manual dashboard forms)."""
    return rule_manager.add_rule(rule)

@app.put("/rules/{rule_id}", response_model=Rule)
def update_rule(rule_id: int, updated_rule: Rule):
    """Updates an existing rule (e.g., toggling it on/off)."""
    rule = rule_manager.update_rule(rule_id, updated_rule)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@app.delete("/rules/{rule_id}")
def delete_rule(rule_id: int):
    """Deletes a rule by its ID."""
    success = rule_manager.delete_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"message": "Rule deleted successfully"}

# --- NLP Endpoint ---

@app.post("/generate-rule", response_model=Rule)
def generate_rule_from_nlp(prompt: NLPPrompt):
    """
    Takes natural language text, passes it to the LLM, validates the JSON, 
    and saves it to the database automatically.
    """
    new_rule = rule_manager.generate_rule_from_text(prompt.text)
    
    if not new_rule:
        raise HTTPException(status_code=400, detail="LLM failed to generate a valid rule from the provided text.")
        
    return new_rule

# --- Alerts & WebSockets ---

@app.get("/alerts", response_model=List[Alert])
def get_alerts():
    """Legacy polling endpoint for alerts."""
    return latest_alerts

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    """
    Real-time WebSocket endpoint. The frontend dashboard connects here 
    to instantly receive alerts the millisecond YOLO triggers them.
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep the connection open and wait for incoming messages (if any)
            # We don't expect the client to send much, mostly just listen.
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

@app.get("/status")
def get_status():
    return {"status": "Backend API is running flawlessly."}