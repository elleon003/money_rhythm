from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def abs_value(value):
    """Returns the absolute value"""
    try:
        return abs(value)
    except (TypeError, ValueError):
        return value

@register.filter
def sum(qs, field):
    """Sum a queryset by field"""
    if not qs:
        return 0
    return sum(getattr(item, field) for item in qs)

@register.filter
def sub(value1, value2):
    """Subtract value2 from value1"""
    try:
        return Decimal(str(value1)) - Decimal(str(value2))
    except (TypeError, ValueError):
        return 0