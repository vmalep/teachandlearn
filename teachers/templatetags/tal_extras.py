from django import template

register = template.Library()


@register.filter
def star_range(rating):
    if rating is None:
        return (0, 5)
    filled = round(float(rating))
    return (filled, 5 - filled)


@register.simple_tag(takes_context=True)
def other_party(context, conversation):
    """Return the conversation participant who is not the current user."""
    user = context["user"]
    return conversation.teacher if user == conversation.student else conversation.student
