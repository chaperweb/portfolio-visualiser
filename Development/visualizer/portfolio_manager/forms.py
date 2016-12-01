from django import forms

class ProjectForm(forms.Form):
    name = forms.CharField(label = 'Name', max_length=50, required = True,
                            error_messages={'required': 'Your project needs a name!'})
    organization = forms.CharField(label = 'Organization', max_length=50, required = True,
                            error_messages={'required': 'Your project needs an Organization!'})
    #startTime = forms.DateTimeField(label = 'Start Date', required = True,
    #                        error_messages={'required': 'When will the project start?'})
    #duration = forms.IntegerField()
