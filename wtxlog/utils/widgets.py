# -*- coding: utf-8 -*-

from wtforms import fields, widgets


# Define wtforms widget and field
class MarkitupTextAreaWidget(widgets.TextArea):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_', 'markitup')
        return super(MarkitupTextAreaWidget, self).__call__(field, **kwargs)


class MarkitupTextAreaField(fields.TextAreaField):
    widget = MarkitupTextAreaWidget()


# Define wtforms widget and field
class CKTextAreaWidget(widgets.TextArea):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)


class CKTextAreaField(fields.TextAreaField):
    widget = CKTextAreaWidget()
