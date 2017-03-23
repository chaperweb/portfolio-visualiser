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

class DimensionForm(ModelForm):

    def __init__(self, project_form, *args, **kwargs):
        super(DimensionForm, self).__init__(*args, **kwargs)
        self.project_form = project_form

    def save(self, *args, **kwargs):
        instance = super(TextDimensionForm, self).save(*args, **kwargs)
        project_dimension = ProjectDimension()
        project_dimension.project = self.project_form.instance
        project_dimension.dimension_object = instance
        project_dimension.save()
        return instance

class TextDimensionForm(DimensionForm):

    class Meta:
        model = TextDimension
        fields = ('value',)
        widgets = {
            'value': forms.TextInput(),
        }

    def __init__(self, name, project_form, *args, **kwargs):
        
        super(TextDimensionForm, self).__init__(project_form, *args, **kwargs)
        self.fields['value'].label = name

class DecimalDimensionForm(DimensionForm):

    class Meta:
        model = DecimalDimension
        fields = ('value',)
      
    def __init__(self, name, project_form, *args, **kwargs):
        super(DecimalDimensionForm, self).__init__(project_form, *args, **kwargs)
        self.fields['value'].label = name
    
class DateDimensionForm(DimensionForm):

    class Meta:
        model = DateDimension
        fields = ('value',)
        widgets = {
            'value': forms.DateInput({'input_type': 'date', 'class': 'datepicker'}),
        }

    def __init__(self, name, project_form, *args, **kwargs):
        
        super(DateDimensionForm, self).__init__(project_form, *args, **kwargs)
        self.fields['value'].label = name

class AssociatedPersonDimensionForm(DimensionForm):

    class Meta:
        model = AssociatedPersonDimension
        fields = ('value',)

    def __init__(self, name, project_form, *args, **kwargs):
        
        super(AssociatedPersonDimensionForm, self).__init__(project_form, *args, **kwargs)
        self.fields['value'].label = name
    

class AssociatedOrganizationDimensionForm(DimensionForm):

    class Meta:
        model = AssociatedOrganizationDimension
        fields = ('value',)

    def __init__(self, name, project_form, *args, **kwargs):
        
        super(AssociatedOrganizationDimensionForm, self).__init__(project_form, *args, **kwargs)
        self.fields['value'].label = name

class AssociatedPersonsDimensionForm(DimensionForm):

    class Meta:
        model = AssociatedPersonsDimension
        fields = ('persons',)

    def __init__(self, name, project_form, *args, **kwargs):
        
        super(AssociatedPersonsDimensionForm, self).__init__(project_form, *args, **kwargs)
        self.fields['persons'].label = name

class AssociatedProjectsDimensionForm(DimensionForm):

    class Meta:
        model = AssociatedProjectsDimension
        fields = ('projects',)

    def __init__(self, name, project_form, *args, **kwargs):
        
        super(AssociatedProjectsDimensionForm, self).__init__(project_form, *args, **kwargs)
        self.fields['projects'].label = name
    

class AddProjectForm(ModelForm):

    organization = forms.ModelChoiceField(queryset=Organization.objects.all(), required=False)

    class Meta:
        model = Project
        fields = ['name','parent']
        labels = {
            "parent": "Organization",
        }
        widgets = {
            "parent": forms.HiddenInput()
        }

    def disable_name_and_organization(self):
        self.fields['organization'].widget.attrs['disabled'] = True
        self.fields['name'].widget.attrs['readonly'] = 'readonly'

