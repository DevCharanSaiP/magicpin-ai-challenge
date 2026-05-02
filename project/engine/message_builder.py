def build_message(intent, merchant, category, trigger, customer):

    name = merchant["identity"]["owner_first_name"]

    if intent == "INSIGHT":
        return f"Dr. {name}, new research relevant to your patients just came in. Want a quick summary?"

    if intent == "FIX_PERFORMANCE":
        ctr = merchant["performance"]["ctr"]
        return f"Your CTR is {ctr:.2%}, below peers. Want to run an offer to improve conversions?"

    if intent == "CONVERT_CUSTOMER" and customer:
        cname = customer["identity"]["name"]
        return f"Hi {cname}, it's time for your next visit. Want to book a slot?"

    if intent == "RETAIN":
        days = merchant["subscription"]["days_remaining"]
        return f"Your plan expires in {days} days. Renew now to keep visibility."

    return "Want help growing your business today?"