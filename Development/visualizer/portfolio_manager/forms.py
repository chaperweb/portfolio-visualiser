from django import forms
from portfolio_manager.models import *
import numbers
from django.forms import ModelForm

class GoogleSheetForm(ModelForm):
    class Meta:
        model = GoogleSheet
        fields = ['name','url']

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


class OrgForm(forms.Form):
    orgs = forms.ModelChoiceField(queryset=Organization.objects.all().order_by('name'),empty_label="Select an organization",
    widget=forms.Select(attrs={"onChange":'submit()'}))
