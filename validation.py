import re
from datetime import datetime
from typing import Dict, Tuple

DATE_FORMAT = "%Y-%m-%d"
PHONE_PATTERN = re.compile(r"^\+?[0-9]{8,15}$")


def validate_user(user_data: Dict[str, str]) -> Tuple[bool, str]:
    """Validate user fields before database operations."""
    required_fields = {
        "first_name": "First name",
        "last_name": "Last name",
        "birth_date": "Birth date",
        "birth_place": "Birth place",
        "phone_number": "Phone number",
    }

    for field, label in required_fields.items():
        if not user_data.get(field, "").strip():
            return False, f"{label} cannot be empty."

    try:
        datetime.strptime(user_data["birth_date"], DATE_FORMAT)
    except ValueError:
        return False, "Birth date must use the format YYYY-MM-DD, for example 2002-04-18."

    if not PHONE_PATTERN.match(user_data["phone_number"].strip()):
        return False, "Phone number must contain 8 to 15 digits and may start with +."

    return True, "Valid user data."
