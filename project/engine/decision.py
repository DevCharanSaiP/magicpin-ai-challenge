def decide_intent(trigger):
    kind = trigger.get("kind")

    if kind == "research_digest":
        return "INSIGHT"

    if kind == "recall_due":
        return "CONVERT_CUSTOMER"

    if kind == "perf_dip":
        return "FIX_PERFORMANCE"

    if kind == "renewal_due":
        return "RETAIN"

    return "GENERAL"