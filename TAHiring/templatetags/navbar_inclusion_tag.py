from django import template
from django.core.urlresolvers import resolve, Resolver404
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.conf import settings

import re

register = template.Library()

@register.inclusion_tag('Problems/navbar_inclusion_tag.html', takes_context = True)
def generate_navbar(context):
    return ''


@register.simple_tag
def check_active(request, view_name):
    if not request:
        return ''
    try:
        if view_name in resolve(request.path_info).url_name:
            return 'active'
        else:
            return ''
    except Resolver404:
        return ''
