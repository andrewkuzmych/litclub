# -*- coding: utf-8 -*-

from django.template import Library, Node
from django.utils.dateformat import DateFormat
import datetime, time
import re

from django.conf import settings

register = Library()

class PaginatorNode(Node):
    def render(self, context):
        paginator = context['paginator']
        page_number = context['page']
        class_name = ''

        if settings.LANGUAGE_CODE == 'uk':
            next_text = u'наступна →'
            previous_text = u'← попередня'
            if paginator.has_next_page(page_number - 1):
                next_link = u'<a href="?page=%s" rel="nofollow">%s</a> ' % (page_number + 1, next_text)
            else:
                next_link = u'наступна →'
            pages_text = u'<span style="color: gray;">сторінка %s з %s</span> ' % (page_number, paginator.pages)
            if paginator.has_previous_page(page_number - 1):
                previous_link = u'<a href="?page=%s" rel="nofollow">%s</a> ' % (page_number - 1, previous_text)
            else:
                previous_link = u'← попередня'
        else:
            next_text = u'следующая →'
            previous_text = u'← предыдущая'
            if paginator.has_next_page(page_number - 1):
                next_link = u'<a href="?page=%s" rel="nofollow">%s</a> ' % (page_number + 1, next_text)
            else:
                next_link = u'следующая →'
            pages_text = u'<span style="color: gray;">страница %s из %s</span> ' % (page_number, paginator.pages)
            if paginator.has_previous_page(page_number - 1):
                previous_link = u'<a href="?page=%s" rel="nofollow">%s</a> ' % (page_number - 1, previous_text)
            else:
                previous_link = u'← предыдущая'

        return u'%s %s %s %s' % (class_name, previous_link, pages_text, next_link)

@register.tag
def paginator(parser, token):
    return PaginatorNode()

@register.filter
def cattext(value):
    value = unicode(value)
    if value == '1':
        return u"Проза"
    if value == '2':
        return u"Поезія"
    if value == '3':
        return u"Інше"
    if value == '4':
        return u"Форум"
    if value == '5':
        return u"Рецензії"
    return u"Всі тексти"

@register.filter
def cattextru(value):
    value = unicode(value)
    if value == '1':
        return u"Проза"
    if value == '2':
        return u"Поэзия"
    if value == '3':
        return u"Другое"
    if value == '4':
        return u"Форум"
    if value == '5':
        return u"Критика"
    return u"Все тексты"


last_date = datetime.datetime.now()

@register.filter
def date_today(value, mode=0, padding=21):
    global last_date
    now = DateFormat(datetime.datetime.now())
    date = DateFormat(value)
    yesterday = DateFormat(datetime.date.fromtimestamp(time.time() - 3600 * 24))
    last = DateFormat(last_date)
    last_date = value

    if mode == 1 or mode == 3:
        if date.format('d.m.y') == last.format('d.m.y'):
            return u'<span style="padding-right: %spx">"</span>' % padding

    if now.format('d.m.y') == date.format('d.m.y'):
        if mode == 2 or mode == 3:
            return date.format('H:i')
        else:
            return u"Сьогодні"
    if yesterday.format('d.m.y') == date.format('d.m.y'):
        return u"Вчора"
    return date.format('d.m.y')

@register.filter
def linebreaksp(value):
    "Converts newlines into <p>"
    value = re.sub(r'\r\n|\r|\n', '\n', value) # normalize newlines
    value = value.replace('\n\n', '<br /><br />\n')
    paras = re.split('\n{1,}', value)
    paras = [u'<p>%s</p>' % p.strip() for p in paras]
    value = u'\n'.join(paras)
    return value
