"""Shared validation utilities."""
import re


def validate_iranian_phone(value: str | None) -> str | None:
    """
    Validate Iranian phone number format.
    
    Accepts:
    - 09xxxxxxxxx (11 digits)
    - +98xxxxxxxxxx (with country code)
    
    Returns the validated phone number or None if empty.
    Raises ValueError if format is invalid.
    """
    if value is None or value.strip() == "":
        return None
    
    value = value.strip()
    
    # Iranian phone number patterns
    pattern_09 = r'^09\d{9}$'
    pattern_98 = r'^\+98\d{10}$'
    
    if re.match(pattern_09, value) or re.match(pattern_98, value):
        return value
    
    raise ValueError('شماره تماس باید به فرمت 09xxxxxxxxx یا +98xxxxxxxxxx باشد')


