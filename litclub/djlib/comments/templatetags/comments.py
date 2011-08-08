# -*- coding: utf-8 -*-
from django.template import Library, Node, TokenParser, resolve_variable, loader
from djlib.comments.models import Comment
from django.http import Http404
from django.contrib.contenttypes.models import ContentType

from djlib.captcha.models import Captcha

register = Library()

class CommentListNode(Node):
  def __init__(self, app_label, model, obj_id_lookup_var, var_name):
    self.app_label, self.model = app_label, model
    self.obj_id_lookup_var = obj_id_lookup_var
    self.var_name = var_name

  def _get_comments(self, comments, list, parent, ident):      
    for c in list:
      if c.parent == parent:
        c.ident = ident
        gc_list = self._get_comments([],list,c,ident+1)
        
        c.last = 0
        if not gc_list:
          c.last = 1
        
        # якщо коментар останн≥й в г≥лц≥ та стертий, не додавати його в список
        # (тод≥ не буде глюку, коли останн≥м у г≥лц≥ в≥дображаЇтьс€ "(стертий коментар)", коли п≥сл€ нього Ї ще стертий)
        if not(c.last and c.is_removed):
          comments.append(c)
        
        for gc in gc_list:
          comments.append(gc)
    return comments
  
  def get_comments(self, comments):
    comments = self._get_comments([],comments,None,0)
    if comments:
      max = 1
      for c in comments:
        c.obj = self.obj
        if not self.user.is_anonymous() and (self.user.is_staff or self.user == self.obj.user or self.user == c.user):
          c.can_delete = 1
        if c.ident > max:
          max = c.ident
      ident = int(600/max)
      if ident > 50:
        ident = 50
      for c in comments:
        c.ident = c.ident * ident
    return comments
  
  def render(self,context):
    self.user = context.get('user', '')
    
    obj_id = resolve_variable(self.obj_id_lookup_var, context)
    content_type = ContentType.objects.get(app_label=self.app_label, model=self.model)
    self.obj = content_type.get_object_for_this_type(pk=int(obj_id))
    
    context[self.var_name] = self.get_comments(Comment.objects.filter(object_id=obj_id, content_type__app_label=self.app_label, content_type__model=self.model).order_by('submit_date'))
    return ''
    

class CommentFormNode(Node):
  def __init__(self, app_label, model, obj_id_lookup_var, user):
    self.app_label, self.model = app_label, model
    self.obj_id_lookup_var = obj_id_lookup_var
    self.user = user
  
  def render(self,context):
    if not context.get('user', '').is_authenticated():
      context['sid'] = Captcha.new().sid
    try:
      context['obj_id'] = resolve_variable(self.obj_id_lookup_var, context)
      context['content_id'] = ContentType.objects.get(app_label=self.app_label, model=self.model).id
    except:
      raise Http404
    return loader.get_template('comments/form.html').render(context)  


@register.tag
def get_comment_list(parser, token):
  """
  Gets comments for the given params and populates the template context with a
  special comment_package variable, whose name is defined by the ``as``
  clause.

  Syntax::

      {% get_comment_list for app_label.model context_var_containing_obj_id as varname (reversed) %}

  Example usage::

      {% get_comment_list for lcom.eventtimes event.id as comment_list %}

  To get a list of comments in reverse order -- that is, most recent first --
  pass ``reversed`` as the last param.
  """
  tokenparser = TokenParser(token.contents)
  if tokenparser.tag() != 'for':
      raise template.TemplateSyntaxError, "'get_comment_list' requires 'for' as the first parameter"
  (app_label, model) = tokenparser.tag().split('.')
  obj_id_lookup_var = tokenparser.tag()
  if tokenparser.tag() != 'as':
      raise template.TemplateSyntaxError, "'get_comment_list' requires 'as' before the variable name to set"
  var_name = tokenparser.tag()
  return CommentListNode(app_label, model, obj_id_lookup_var, var_name)
  
@register.tag
def get_comment_form(parser, token):
  tokenparser = TokenParser(token.contents)
  if tokenparser.tag() != 'for':
      raise template.TemplateSyntaxError, "'get_comment_form' requires 'for' as the first parameter"
  (app_label, model) = tokenparser.tag().split('.')
  obj_id_lookup_var = tokenparser.tag()
  
  if tokenparser.tag() != 'user':
      raise template.TemplateSyntaxError, "'get_comment_form' requires 'user'"
  user = tokenparser.tag()
  
  return CommentFormNode(app_label, model, obj_id_lookup_var, user)