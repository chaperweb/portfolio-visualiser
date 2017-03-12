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


class CronForm(forms.Form):
    orgs = forms.ModelChoiceField(queryset=Organization.objects.all().order_by('name'),empty_label="(Nothing)",
    widget=forms.Select(attrs={"onChange":'submit()'}))

class TableSpecification(forms.Form):
    name = forms.CharField(label = 'Field name', max_length=50, required = True,
                            error_messages={'required': 'Your field needs a name!'})
    DATATYPES = (('TXT', 'Teksti'),('NUM', 'Numeerinen'),('DEC','Desimaali'))
    datatype = forms.ChoiceField(choices=DATATYPES)
    value = forms.CharField(label = 'Value', max_length=64, required = True,
                            error_messages={'required': 'value!'})

    def clean(self):
        cleaned_data = super(TableSpecification, self).clean()
        name = cleaned_data.get("name")
        datatype = cleaned_data.get("datatype")
        value = cleaned_data.get("value")

        if datatype == 'NUM':
            try:
                val = int(value)
            except ValueError:
                raise forms.ValidationError(
                    "ERROERRORERROR."
                )
                print("That's not an int!")

            if not isinstance(val, numbers.Number):
                raise forms.ValidationError(
                    "ERROERRORERROR."
                )
        if datatype == 'DEC':
            try:
                val = float(value)
            except ValueError:
                raise forms.ValidationError(
                    "ERROERRORERROR."
                )
                print("That's not an int!")

            if not isinstance(val, numbers.Number):
                raise forms.ValidationError(
                    "ERROERRORERROR."
                )

class OrgForm(forms.Form):
    name = forms.CharField(label = 'Name', max_length=50, required = True,
                                error_messages={'required': 'Your project needs a name!'})
    orgs = forms.ModelChoiceField(queryset=Organization.objects.all().order_by('name'),empty_label="(Nothing)")



class AddProjectForm(forms.Form):


    def fieldsbyorg(self, *args, **kwargs):

        projs = Project.objects.filter(parent=args)
        #print(len(projs))
        dimensions = []
        dims = {}

        for p in projs:
            dimensions += ProjectDimension.objects.filter(project=p)

        # print(len(dimensions))
        for dim in dimensions:
            #print(dim.dimension_object.name)
            #print(dim.dimension_object.name != "ProjectOwner" and dim.dimension_object.name != "ProjectDependencies" and dim.dimension_object.name != "ProjectManger" and dim.dimension_object.name != "Members")
            if dim.dimension_object.name not in dims:
                # and dim.dimension_object.name != "ProjectOwner" and dim.dimension_object.name != "ProjectDependencies" and dim.dimension_object.name != "ProjectManager" and dim.dimension_object.name != "Members":

                dims[dim.dimension_object.name] = dim
            #    print(dims[dim.dimension_object.name])
                print("täällä")

                print(dims[dim.dimension_object.name])
                if(str(dims[dim.dimension_object.name]) == "TextDimension"
                or dims[dim.dimension_object.name] == "AssociatedPersonDimension"
                or dims[dim.dimension_object.name] == "AssociatedPersonsDimension"
                or dims[dim.dimension_object.name] == "AssociatedOrganizationDimension"
                or dims[dim.dimension_object.name] == "AssociatedProjectsDimension"):
                    print("here")
                    self.fields[dim.dimension_object.name] = forms.CharField()
                elif (str(dims[dim.dimension_object.name]) == "DateDimension"):
                    self.fields[dim.dimension_object.name] = forms.DateTimeField()
                elif (str(dims[dim.dimension_object.name]) == "DecimalDimension"):
                    self.fields[dim.dimension_object.name] = forms.DecimalField()



    def __init__(self, projOrg, *args, **kwargs):
        super(AddProjectForm, self).__init__(*args, **kwargs)
        self.fieldsbyorg(projOrg)
