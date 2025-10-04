from django import template

register = template.Library()

@register.filter
def pluck(objects, attr_name):
    return [getattr(obj, attr_name, None) for obj in objects]
