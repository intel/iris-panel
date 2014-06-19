from django import template

register = template.Library()


@register.filter
def user_display_name(user):
    names = []
    if user.last_name:
        names.append(user.last_name)
    if user.first_name:
        names.append(user.first_name)
    if names:
        return ', '.join(names)
    return user.username.split('@', 1)[0]
