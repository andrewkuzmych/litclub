# -*- coding: utf-8 -*-

from django.newforms.forms import BoundField
from django.utils.html import escape 
from django import newforms as forms
from django.newforms.util import flatatt, StrAndUnicode, smart_unicode
from django.utils import simplejson


class AutoCompleteWidget(forms.Widget):
  def __init__(self, values=[], tokens=None, minChars=1, attrs=None):
    self.values = values
    self.tokens = tokens
    self.minChars = minChars
    self.attrs = attrs or {}
    
  def render(self, name, value, attrs=None):
    if not value: value = ""
    value = smart_unicode(value)

    values = simplejson.dumps(self.values,ensure_ascii=False)
    
    if not self.tokens: tokens = ""
    if self.tokens: tokens = ", tokens: '%s'" % self.tokens
    
    if not self.minChars: minChars = ""
    if self.minChars: minChars = ", minChars: '%s'" % self.minChars
    s = u''
    return u"""<input id="id_%s" name="%s" value="%s" type="text" autocomplete="off" %s>
    <div id="id_%supdate" class=autocomplete style="display:none;border:1px solid black;background-color:white;height:150px;overflow:auto;"></div>
           <script type="text/javascript" language="javascript" charset="utf-8">
           // <![CDATA[
             new Autocompleter.Local('id_%s','id_%supdate', %s, { fullSearch: true, partialSearch: true, frequency:0.001 %s %s });
           // ]]>
           </script>""" % (name, name, value, flatatt(self.attrs), name, name, name, values, minChars, tokens)

def _html_output(self, normal_row, error_row, row_ender, help_text_html, errors_on_separate_row):
    "Helper function for outputting HTML. Used by as_table(), as_ul(), as_p()."
    top_errors = self.non_field_errors() # Errors that should be displayed above all fields.
    output, hidden_fields = [], []
    for name, field in self.fields.items():
        bf = BoundField(self, field, name)
        bf_errors = bf.errors # Cache in local variable.
        if bf.is_hidden:
            if bf_errors:
                top_errors.extend(['(Hidden field %s) %s' % (name, e) for e in bf_errors])
            hidden_fields.append(unicode(bf))
        else:
            if errors_on_separate_row and bf_errors:
                output.append(error_row % bf_errors)
            label = bf.label and bf.label_tag(escape(bf.label + ':')) or ''
            if field.help_text:
                help_text = help_text_html % field.help_text
            else:
                #raise Exception(field.widget.attrs.get('xxx',''))
                help_text = u''
            #s = unicode(bf)
            #raise Exception( repr(s) )
            output.append(normal_row % {'errors': bf_errors, 'label': label, 'field': unicode(bf), 'help_text': help_text})
    if top_errors:
        output.insert(0, error_row % top_errors)
    if hidden_fields: # Insert any hidden fields in the last row.
        str_hidden = u''.join(hidden_fields)
        if output:
            last_row = output[-1]
            # Chop off the trailing row_ender (e.g. '</td></tr>') and insert the hidden fields.
            output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
        else: # If there aren't any rows in the output, just append the hidden fields.
            output.append(str_hidden)
    return u'\n'.join(output)

def as_div(form):
  return _html_output(form,u'<div>%(label)s %(field)s %(errors)s <small>%(help_text)s</small></div>', u'<div>%s</div>', '</div>', u' %s', False)
