from django import template
from portfolio_manager.models import Employees, OrganizationAdmins

register = template.Library()

@register.filter
def is_orgadmin(user):
    groups = user.groups.all()
    for g in groups:
        if str(g).endswith('_OrgAdmins'):
            return True
    return False
