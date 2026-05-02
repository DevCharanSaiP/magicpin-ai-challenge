from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

from engine.state import state
from engine.compose import compose

app = FastAPI()

# -------------------------------
# Models
# -------------------------------

class ContextRequest(BaseModel):
    scope: str
    context_id: str
    version: int
    payload: Dict[str, Any]
    delivered_at: str


class TickRequest(BaseModel):
    now: str
    available_triggers: List[str]


class ReplyRequest(BaseModel):
    conversation_id: str
    merchant_id: str
    customer_id: Optional[str]
    from_role: str
    message: str
    received_at: str


@app.get("/")
def root():
    return {"message": "Vera AI Bot is running"}

# -------------------------------
# Endpoints
# -------------------------------

@app.get("/v1/healthz")
def healthz():
    return {
        "status": "ok",
        "uptime_seconds": 100,
        "contexts_loaded": {
            "category": len(state["categories"]),
            "merchant": len(state["merchants"]),
            "customer": len(state["customers"]),
            "trigger": len(state["triggers"]),
        }
    }


@app.get("/v1/metadata")
def metadata():
    return {
        "team_name": "AI Builders",
        "team_members": ["You"],
        "model": "deterministic-rule-engine",
        "approach": "rule-based intent + templated message composition",
        "contact_email": "your@email.com",
        "version": "1.0.0",
        "submitted_at": datetime.utcnow().isoformat()
    }


@app.post("/v1/context")
def context(req: ContextRequest):
    scope_map = {
        "category": "categories",
        "merchant": "merchants",
        "customer": "customers",
        "trigger": "triggers"
    }

    if req.scope not in scope_map:
        return {"accepted": False, "reason": "invalid_scope"}

    store = state[scope_map[req.scope]]

    existing = store.get(req.context_id)

    if existing and existing["version"] > req.version:
        return {
            "accepted": False,
            "reason": "stale_version",
            "current_version": existing["version"]
        }

    store[req.context_id] = {
        "version": req.version,
        "data": req.payload
    }

    return {
        "accepted": True,
        "ack_id": f"ack_{req.context_id}_v{req.version}",
        "stored_at": datetime.utcnow().isoformat()
    }


@app.post("/v1/tick")
def tick(req: TickRequest):
    actions = []

    for trigger_id in req.available_triggers:
        trigger_entry = state["triggers"].get(trigger_id)
        if not trigger_entry:
            continue

        trigger = trigger_entry["data"]

        merchant = state["merchants"][trigger["merchant_id"]]["data"]
        category = state["categories"][merchant["category_slug"]]["data"]

        customer = None
        if trigger.get("customer_id"):
            cust_entry = state["customers"].get(trigger["customer_id"])
            if cust_entry:
                customer = cust_entry["data"]

        result = compose(category, merchant, trigger, customer)

        actions.append({
            "conversation_id": f"conv_{trigger_id}",
            "merchant_id": trigger["merchant_id"],
            "customer_id": trigger.get("customer_id"),
            "send_as": result["send_as"],
            "trigger_id": trigger_id,
            "body": result["message"],
            "cta": result["cta"],
            "suppression_key": result["suppression_key"],
            "rationale": result["rationale"]
        })

    return {"actions": actions}


@app.post("/v1/reply")
def reply(req: ReplyRequest):
    # simple deterministic response
    merchant = state["merchants"][req.merchant_id]["data"]
    category = state["categories"][merchant["category_slug"]]["data"]

    trigger = {
        "kind": "reply_followup",
        "merchant_id": req.merchant_id,
        "customer_id": req.customer_id,
        "payload": {}
    }

    customer = None
    if req.customer_id:
        customer = state["customers"][req.customer_id]["data"]

    result = compose(category, merchant, trigger, customer)

    return {
        "body": result["message"],
        "cta": result["cta"],
        "send_as": result["send_as"],
        "suppression_key": result["suppression_key"],
        "rationale": result["rationale"]
    }