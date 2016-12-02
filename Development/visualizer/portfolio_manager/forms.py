from django import forms
from portfolio_manager.models import Organization

class ProjectForm(forms.Form):
    name = forms.CharField(label = 'Name', max_length=50, required = True,
                            error_messages={'required': 'Your project needs a name!'})
    organization = forms.CharField(label = 'Organization', max_length=50, required = True,
                            error_messages={'required': 'Your project needs an Organization!'})
    #startTime = forms.DateTimeField(label = 'Start Date', required = True,
    #                        error_messages={'required': 'When will the project start?'})
    #duration = forms.IntegerField()

class OrganizationForm(forms.Form):
    name = forms.CharField(label = 'Name', max_length=50, required = True,
                            error_messages={'required': 'Your organization needs a name!'})

class CronForm(forms.Form):
    orgs = forms.ModelChoiceField(queryset=Organization.objects.all().order_by('name'),empty_label="(Nothing)",to_field_name="name")
    
