from django import forms
from portfolio_manager.models import Organization, Project, Person

class ProjectForm(forms.Form):
    name = forms.CharField(label = 'Name', max_length=50, required = True,
                            error_messages={'required': 'Your project needs a name!'})
    organization = forms.ModelChoiceField(queryset=Organization.objects.all())
    owner = forms.ModelChoiceField(queryset=Person.objects.all())
    budget = forms.DecimalField(max_digits=20, decimal_places=2)


class OrganizationForm(forms.Form):
    name = forms.CharField(label = 'Name', max_length=50, required = True,
                            error_messages={'required': 'Your organization needs a name!'})

class PersonForm(forms.Form):
    first = forms.CharField(label = 'First Name', max_length=50, required = True,
                            error_messages={'required': 'Your person needs a name!'})
    last = forms.CharField(label = 'Last Name', max_length=50, required = True,
                                error_messages={'required': 'Your person needs a name!'})

    # def __init__(self):
    #


class CronForm(forms.Form):
    orgs = forms.ModelChoiceField(queryset=Organization.objects.all().order_by('name'),empty_label="(Nothing)")
