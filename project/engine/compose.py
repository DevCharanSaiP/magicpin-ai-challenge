from engine.decision import decide_intent
from engine.message_builder import build_message


def compose(category, merchant, trigger, customer=None):
    intent = decide_intent(trigger)

    message = build_message(intent, merchant, category, trigger, customer)

    return {
        "message": message,
        "cta": "Reply YES",
        "send_as": "vera",
        "suppression_key": trigger.get("suppression_key", "default"),
        "rationale": f"Intent={intent} based on trigger={trigger.get('kind')}"
    }