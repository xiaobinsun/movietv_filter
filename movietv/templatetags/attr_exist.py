from django import template

register = template.Library()

@register.simple_tag
def attr_exist(obj, sattr):
    return sattr in obj
