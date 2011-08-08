# -*- coding: utf-8 -*-
# кирилиця
from django.template import Library, Node
from html_filter import html_filter

register = Library()

@register.filter
def some_html(value):
    filter = html_filter()
    filter.allowed['s'] = ()
    filter.allowed['strike'] = ()
    filter.allowed['font'] = ('color', 'face')

    value = filter.go(value)
    return value