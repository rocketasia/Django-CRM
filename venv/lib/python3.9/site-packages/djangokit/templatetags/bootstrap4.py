#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the same license as the current project.
#
from django.forms.fields import BooleanField, NullBooleanField
from django.template import Library
from django.utils.encoding import force_str
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe


register = Library()


@register.filter
def form_group(bound, fgclass=''):
    """
    Formed HTML for visible fields of a forms (boundfield).
    """
    field = bound.field
    if field.__class__.__name__ == 'ReCaptchaField':
        return mark_safe('<div>%s</div>' % force_str(bound))
    is_nullbool = isinstance(field, NullBooleanField)
    is_checkbox = not is_nullbool and isinstance(field, BooleanField)
    if is_checkbox:
        html = (
            '<div class="form-group %(fgclass)s %(error_class)s">'
            '<div class="checkbox">'
            '<label>%(widget)s %(label)s</label>'
            '%(errors)s'
            '%(help)s'
            '</div>'
            '</div>'
        )
    else:
        html = (
            '<div class="form-group %(fgclass)s %(error_class)s">'
            '%(label)s'
            '%(widget)s'
            '%(errors)s'
            '%(help)s'
            '</div>'
        )
    kw = {'error_class': '', 'errors': '', 'help': '', 'fgclass': fgclass}
    if is_checkbox:
        kw['widget'] = force_str(bound)
        kw['label'] = force_str(bound.label)
    else:
        widget = field.widget
        attrs = widget.attrs
        input_type = getattr(widget, 'input_type', None)
        skip_types = ('hidden', 'file', 'checkbox', 'select', 'radio')
        if 'placeholder' not in attrs and input_type not in skip_types:
            attrs['placeholder'] = force_str(bound.label)
        classes = [c for c in attrs.get('class', '').split(' ') if c]
        if 'form-control' not in classes:
            classes.insert(0, 'form-control')
        attrs['class'] = ' '.join(classes)
        kw['widget'] = bound.as_widget(attrs=attrs)
        label = ''
        if bound.label:
            if field.required:
                label = '<strong>' + bound.label_tag() + '</strong>'
            else:
                label = bound.label_tag()
        kw['label'] = label
    if bound.errors:
        kw['error_class'] = 'text-danger'
        errors = bound.errors.as_data()
        kw['errors'] = format_html(
            '<ul class="text-danger mt-2">{}</ul>',
            format_html_join('', '<li>{}</li>', [e for e in errors])
        )
    if bound.help_text:
        kw['help'] = '<small class="form-text text-muted">%s</small>' % bound.help_text
    return mark_safe(html % kw)
