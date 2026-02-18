from django import template
import locale

register = template.Library()

@register.filter
def currency(value):
    """Format a number as currency with commas"""
    try:
        value = float(value)
        # Format with commas and 2 decimal places
        return f"₦{value:,.2f}"
    except (ValueError, TypeError):
        return "₦0.00"

@register.filter
def commafy(value):
    """Add commas to a number without currency symbol"""
    try:
        value = float(value)
        return f"{value:,.2f}"
    except (ValueError, TypeError):
        return "0.00"