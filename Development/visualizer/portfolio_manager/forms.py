from django import forms
from portfolio_manager.models import *
import numbers
from django.forms import ModelForm

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

class OrgForm(forms.Form):
    orgs = forms.ModelChoiceField(queryset=Organization.objects.all().order_by('name'),empty_label="Select an organization",
    widget=forms.Select(attrs={"onChange":'submit()'}))

class DimensionForm(ModelForm):

    def __init__(self, *args, project_form=None, dimension_name='', **kwargs):
        super(DimensionForm, self).__init__(*args, **kwargs)
        self.project_form = project_form
        self.dimension_name = dimension_name

    def save(self, *args, **kwargs):
        self.instance.name = self.dimension_name
        instance = super(DimensionForm, self).save(*args, **kwargs)

        # Create for each XyxDimension model instance ProjectDimension that
        # glues project together with XyxDimension
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

    def __init__(self, *args, **kwargs ):
        super(TextDimensionForm, self).__init__(label_suffix='', *args, **kwargs)
        self.fields['value'].label = self.dimension_name

class DecimalDimensionForm(DimensionForm):

    class Meta:
        model = DecimalDimension
        fields = ('value',)

    def __init__(self, *args, **kwargs):
        super(DecimalDimensionForm, self).__init__(label_suffix='', *args, **kwargs)
        self.fields['value'].label = self.dimension_name

class DateDimensionForm(DimensionForm):

    value = forms.DateField(input_formats=["%d/%m/%Y"])

    class Meta:
        model = DateDimension
        fields = ('value',)

    def __init__(self, *args, **kwargs):
        super(DateDimensionForm, self).__init__(label_suffix='', *args, **kwargs)
        self.fields['value'].label = self.dimension_name
        self.fields['value'].widget.attrs['class'] = 'datepicker'

class AssociatedPersonDimensionForm(DimensionForm):

    class Meta:
        model = AssociatedPersonDimension
        fields = ('value',)

    def __init__(self, *args, **kwargs):
        super(AssociatedPersonDimensionForm, self).__init__(label_suffix='', *args, **kwargs)
        self.fields['value'].label = self.dimension_name


class AssociatedOrganizationDimensionForm(DimensionForm):

    class Meta:
        model = AssociatedOrganizationDimension
        fields = ('value',)

    def __init__(self, *args, **kwargs):
        super(AssociatedOrganizationDimensionForm, self).__init__(label_suffix='', *args, **kwargs)
        self.fields['value'].label = self.dimension_name

class AssociatedPersonsDimensionForm(DimensionForm):

    class Meta:
        model = AssociatedPersonsDimension
        fields = ('value',)

    def __init__(self, *args, **kwargs):
        super(AssociatedPersonsDimensionForm, self).__init__(label_suffix='', *args, **kwargs)
        self.fields['value'].label = self.dimension_name

class AssociatedProjectsDimensionForm(DimensionForm):

    class Meta:
        model = AssociatedProjectsDimension
        fields = ('projects',)

    def __init__(self, *args, **kwargs):
        super(AssociatedProjectsDimensionForm, self).__init__(label_suffix='', *args, **kwargs)
        self.fields['projects'].label = self.dimension_name

class AddProjectForm(ModelForm):

    # Current implementation requires that the organization (parent field) and name are
    # rendered as read-only fields on "Add project" page.
    # The only way to render dropdown select as read-only is to mark it 'disabled'
    # Disabled <select> is not sent within POST data. Organization field is only for
    # displaying selected organization and data that is saved to db is sent with hidden
    # field

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

    def __init__(self, *args, **kwargs):
        super(AddProjectForm, self).__init__(label_suffix='', *args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Project name'
        self.fields['organization'].widget.attrs['required'] = True

    def disable_name_and_organization(self):
        self.fields['organization'].widget.attrs['disabled'] = True
        self.fields['name'].widget.attrs['readonly'] = 'readonly'

class ProjectTemplateForm(ModelForm):
    # Can we filter these with some attribute?
    base_types = [
        "textdimension",
        "datedimension",
        "associatedpersondimension",
        "associatedpersonsdimension",
        "associatedorganizationdimension",
        "associatedprojectsdimension",
        "decimaldimension"
    ]
    cts = ContentType.objects.filter(model__in = base_types)
    field_type = forms.ModelChoiceField(queryset=cts, required=True)

    class Meta:
        model = ProjectTemplate
        fields = ['name', 'organization']
        labels = {
            "name": "Name",
            "organization": "Organization",
        }
        widgets = {
            "organization": forms.HiddenInput()
        }
