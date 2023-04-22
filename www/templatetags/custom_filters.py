# templatetags/custom_filters.py

from django import template
from www.models import Department

register = template.Library()

@register.filter
def is_department_head(user):
    department = Department.objects.filter(head=user).first()
    return department is not None
