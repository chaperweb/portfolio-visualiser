from django.shortcuts import render, redirect, get_object_or_404
from portfolio_manager.models import *
from portfolio_manager.forms import *
from django.contrib.contenttypes.models import ContentType
import logging
from django.http import JsonResponse
from portfolio_manager.serializers import ProjectSerializer
from portfolio_manager.importer import from_google_sheet

# LOGGING
logger = logging.getLogger('django.request')

# Site to see history of projects
def history(request):
    history_all = Project.history.all()
    names = {}
    orgs = {}
    dates = {}
    for h in history_all:
        names[h.id] = []
        orgs[h.id] = []
        dates[h.id] = []
    for h in history_all:
        names[h.id].append(h.name)
        orgs[h.id].append(h.parent)
        dates[h.id].append(h.history_date)

    return render(request, 'history.html', {'ids':range(1, len(names)+1), 'names':names, 'orgs':orgs, 'dates':dates})

# Site to upload a new project
def add_new_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            # Save a new Organization
            organization = Organization(name = form.cleaned_data['organization'])
            organization.save()

            # Save a new Project
            newproject = Project(name = form.cleaned_data['name'], parent = organization)
            newproject.save()

            # Make ProjectDimension for owner
            project_dimension_owner = ProjectDimension(dimension_object=newproject, project=newproject)
            project_dimension_owner.save()

            # Make AssociatedPersonDimension
            pers = get_object_or_404(Person, pk=form.cleaned_data['owner'].pk)
            assPerson = AssociatedPersonDimension(value=pers, name=str(pers))
            assPerson.save()

            # Make ProjectOwnerDimension
            own = ProjectOwnerDimension(assPerson=assPerson)
            own.save()

           # Link owner to project
            project_dimension_owner.dimension_object=own
            project_dimension_owner.save()

            #######################
            ####    BUDGET  #######
            #######################

            #Project Dimension for budget
            project_dimension_budget = ProjectDimension(dimension_object=newproject, project=newproject)
            project_dimension_budget.save()

            # Make budjet dimension
            budget = DecimalDimension(name="budget", value=form.cleaned_data['budget'])
            budget.save()

            # Link budget to project
            project_dimension_budget.dimension_object=budget
            project_dimension_budget.save()

            form = ProjectForm()
        return redirect('projects')

    elif request.method == 'GET':
        form = ProjectForm()
    return render(request, 'uploadproject.html', {'form': form})

# Site to add a new organization
def add_new_org(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            organization = Organization(name = form.cleaned_data['name'])
            organization.save()
        return redirect('add_new_project')

    elif request.method == 'GET':
        form = OrganizationForm()
    return render(request, 'new_org.html', {'form':form})

# Site to add a new person
def add_new_person(request):
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            person = Person(first_name=form.cleaned_data['first'], last_name=form.cleaned_data['last'])
            person.save()
        return redirect('add_new_project')

    elif request.method == 'GET':
        form = PersonForm()
    return render(request, 'new_person.html', {'form':form})

# Site to see all projects
def projects(request):
    projects_all = Project.objects.all()
    return render(request, 'projects.html', {'projects': projects_all})

# Site to see all organizations
def organizations(request):
   if request.method == "POST":
      form = CronForm(request.POST)

      if form.is_valid:
         projs = Project.objects.filter(parent=request.POST.get("orgs", ""))

         #redirect to the url where you'll process the input
         return render(request, 'projects_by_organization.html', {'projs':projs}) # insert reverse or url
   else:
        form = CronForm()
   return render(request, 'droptable_organization.html', {'form':form})

def show_project(request, project_id):
        theProject = get_object_or_404(Project, pk=project_id)
        pod = ContentType.objects.get_for_model(ProjectOwnerDimension)
        dd = ContentType.objects.get_for_model(DecimalDimension)
        nd = ContentType.objects.get_for_model(NumericDimension)
        td = ContentType.objects.get_for_model(TextDimension)

        # Default fields
        owner = ProjectDimension.objects.filter(content_type=pod, project_id=theProject.id).first().dimension_object.assPerson.value   # ONLY WORKS IF THERE IS ONLY ONE OWNER
        budget = ProjectDimension.objects.filter(content_type=dd, project_id=theProject.id).first()

        # Added text fields
        texts = ProjectDimension.objects.filter(content_type=td, project_id=theProject.id)

        # Added integer fields
        intfields = ProjectDimension.objects.filter(content_type=nd, project_id=theProject.id)

        # Added decimal fields, removing budget from the query set
        decfields = ProjectDimension.objects.filter(content_type=dd, project_id=theProject.id).exclude(pk=budget.pk)


        return render(request, 'project.html', {'project': theProject, 'owner': owner, 'budget':budget, 'text':texts, 'intfield':intfields, 'decfield':decfields })

def project_edit(request, project_id):
    proj = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            # Update the projects info
            proj.name = form.cleaned_data['name']
            org = get_object_or_404(Organization, name=form.cleaned_data['organization'])
            proj.parent = org
            proj.save()

        return redirect('show_project', project_id=proj.pk)
    else:
        data = { 'name': proj.name, 'parent': proj.parent }
        form = ProjectForm(data)
    return render(request, 'project_edit.html', {'form': form})

def delete_google_sheet(request, google_sheet_id):
    GoogleSheet.objects.get(id=google_sheet_id).delete()
    return redirect('importer')

def load_google_sheet(request, google_sheet_id):
    google_sheet = GoogleSheet.objects.get(id=google_sheet_id)
    from_google_sheet(google_sheet.url)
    return redirect('importer')

def importer(request):
    if request.method == "POST":
        form = GoogleSheetForm(request.POST)

        if form.is_valid():
            form.save()

        return redirect('importer')
    else:
        return render(request, 'importer.html', { 'google_sheets': GoogleSheet.objects.all(), 'form': GoogleSheetForm() } )

def json(request, project_id):
    project = Project.objects.get(pk=project_id)
    serializer = ProjectSerializer(project)
    return JsonResponse(serializer.data)

def insert_field(request, project_id):
    proj = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = TableSpecification(request.POST)
        if form.is_valid():
            if form.cleaned_data['datatype']=='TXT': #Trying to add a text field
                # Project dimension for text
                pd_text = ProjectDimension(dimension_object=proj, project=proj)
                pd_text.save()

                # Make text dimension
                text = TextDimension(name=form.cleaned_data['name'], value=form.cleaned_data['value'])
                text.save()

                # Link text to project
                pd_text.dimension_object=text
                pd_text.save()
                return redirect('show_project', project_id=proj.pk)
            elif form.cleaned_data['datatype']=='DEC': # Trying to add a decimal field
                pd_num = ProjectDimension(dimension_object=proj, project=proj)
                pd_num.save()

                # Make decimal dimension
                dec = DecimalDimension(name=form.cleaned_data['name'], value=form.cleaned_data['value'])
                dec.save()

                # Link decimal to project
                pd_num.dimension_object=dec
                pd_num.save()
                return redirect('show_project', project_id=proj.pk)
            else: # Not text or decimal, so it is integer
                pd_num = ProjectDimension(dimension_object=proj, project=proj)
                pd_num.save()

                # Make numeric dimension
                num = NumericDimension(name=form.cleaned_data['name'], value=form.cleaned_data['value'])
                num.save()

                # Link numeric to project
                pd_num.dimension_object=num
                pd_num.save()
                return redirect('show_project', project_id=proj.pk)
        else: # if form is not valid, return to form again
            formt = TableSpecification()
            return render(request, 'insert_field.html', {'formt':formt})
    elif request.method == 'GET':
        formt = TableSpecification()
        return render(request, 'insert_field.html', {'formt':formt})
