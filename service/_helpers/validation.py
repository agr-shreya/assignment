from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


def phone_validation(value: str):
    validatePhone = RegexValidator(regex=r"^\+?1?\d{8,15}$")

    try:
        validatePhone(value)
        # Valid value, return it
        return value
    except ValidationError:
        raise ValidationError("Please input a valid phone number.")
