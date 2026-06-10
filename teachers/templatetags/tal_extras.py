from django import template

register = template.Library()


@register.filter
def star_range(rating):
    """Return (filled, empty) counts for a 1-5 star rating."""
    if rating is None:
        return (0, 5)
    filled = round(float(rating))
    return (filled, 5 - filled)
