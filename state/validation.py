def validate_user_input(inputs: dict) -> tuple[bool, dict]:
    errors = {}
    
    if not inputs.get("destination", "").strip():
        errors["destination"] = "Destination is required."

    days = inputs.get("days", 0)
    nights = inputs.get("nights", 0)
    budget = inputs.get("budget_rs", 0.0)

    if not isinstance(days, int) or days < 1:
        errors["days"] = "Please enter a valid number of days (minimum 1)."

    if not isinstance(nights, int) or nights < 0:
        errors["nights"] = "Please enter a valid number of nights."
        
    if "nights" not in errors and nights not in [days, days - 1, days + 1]:
        errors["nights"] = "Nights must be equal to days, days - 1, or days + 1."

    if budget <= 0:
        errors["budget_rs"] = "Budget must be greater than ₹0."

    return len(errors) == 0, errors
