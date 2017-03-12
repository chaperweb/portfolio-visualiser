from django.shortcuts import render, redirect, get_object_or_404
from portfolio_manager.models import *
from portfolio_manager.forms import *
from django.contrib.contenttypes.models import ContentType
import logging
from django.http import JsonResponse, HttpResponse
from portfolio_manager.serializers import ProjectSerializer, OrganizationSerializer
from portfolio_manager.importer import from_google_sheet
import json as json_module

# LOGGING
logger = logging.getLogger('django.request')

def home(request):
    context = {}
    context["projects"] = Project.objects.all()
    return render(request, 'homepage.html', context)

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
        data = {'name': request.POST.get('orgName')}
        form = OrganizationForm(data)
        if form.is_valid():
            organization = Organization(name = form.cleaned_data['name'])
            organization.save()

            response_data = {}
            response_data['result'] = 'Created organization successfully!'
            response_data['orgName'] = organization.name
            return HttpResponse(
                json_module.dumps(response_data),
                content_type="application/json"
            )

    return HttpResponse(
        json_module.dumps({"nothing to see": "this isn't happening"}),
        content_type="application/json"
    )

# Site to add a new person
def add_new_person(request):
    if request.method == 'POST':
        data = {'first': request.POST.get('first'), 'last': request.POST.get('last')}
        form = PersonForm(data)
        if form.is_valid():
            person = Person(first_name=form.cleaned_data['first'], last_name=form.cleaned_data['last'])
            person.save()
            response_data = {}
            response_data['result'] = 'Created person successfully!'
            response_data['name'] = person.first_name + " " + person.last_name
            return HttpResponse(
                json_module.dumps(response_data),
                content_type="application/json"
            )
    return HttpResponse(
        json_module.dumps({"nothing to see": "this isn't happening"}),
        content_type="application/json"
    )

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
        dd = ContentType.objects.get_for_model(DecimalDimension)
        td = ContentType.objects.get_for_model(TextDimension)
        dated = ContentType.objects.get_for_model(DateDimension)
        assPersonD = ContentType.objects.get_for_model(AssociatedPersonDimension)
        assPersonsD = ContentType.objects.get_for_model(AssociatedPersonsDimension)
        assOrgD = ContentType.objects.get_for_model(AssociatedOrganizationDimension)
        assProjsD = ContentType.objects.get_for_model(AssociatedProjectsDimension)

        # Default fields
        budget = ProjectDimension.objects.filter(content_type=dd, project_id=theProject.id).first()

        # All dimensions
        dims = ProjectDimension.objects.filter(project_id=theProject.id)
        # Added text fields
        texts = dims.filter(content_type=td)
        # Added decimal fields, removing budget from the query set
        decfields = dims.filter(content_type=dd).exclude(pk=budget.pk)
        # Date dimensions
        dateds = dims.filter(content_type=dated)
        # Associated person dimensions
        assPersonDs = dims.filter(content_type=assPersonD)
        # Associated persons dimensions
        assPersonsDs = dims.filter(content_type=assPersonsD)
        # Associated persons dimensions
        assOrgDs = dims.filter(content_type=assOrgD)
        # Associated projects dimensions
        assProjsDs = dims.filter(content_type=assProjsD)

        context = {}
        context['project'] = theProject
        context['budget'] = budget
        context['text'] = texts
        context['decfield'] = decfields
        context['dates'] = dateds
        context['assPerson'] = assPersonDs
        context['assPersons'] = assPersonsDs
        context['assOrg'] = assOrgDs
        context['assProjs'] = assProjsDs

        context['projects'] = Project.objects.all()

        return render(request, 'project.html', context)

def project_edit(request, project_id, field_name):
    proj = get_object_or_404(Project, pk=project_id)
    if field_name == "Organization":
        try:
            org = Organization.objects.get(name=request.POST.get('name'))
        except Organization.DoesNotExist:
            org = Organization(name=request.POST.get('name'))
            org.save()
        proj.parent = org
        proj.save()
        return JsonResponse({"name": request.POST.get('name')})

    elif field_name == "text":
        ct = ContentType.objects.get_for_model(TextDimension)
        td = ProjectDimension.objects.filter(content_type= ct, project_id=project_id)
        tds = []
        # Manual filtering
        for t in td:
            if t.dimension_object.name == request.POST.get('field'):
                tds = t.dimension_object
                break;
                
        tds.value = request.POST.get('textValue')
        tds.save()
        return JsonResponse({"field": tds.name, "value": tds.value}, safe=True)

    elif field_name == "decimal":
        ct = ContentType.objects.get_for_model(DecimalDimension)
        td = ProjectDimension.objects.filter(content_type= ct, project_id=project_id)
        print(request.POST.get('field'))
        tds = []
        # Manual filtering
        for t in td:
            if t.dimension_object.name == request.POST.get('field'):
                tds = t.dimension_object
                break;

        tds.value = request.POST.get('decValue')
        tds.save()
        return JsonResponse({"field": tds.name, "value": tds.value}, safe=True)

    else:
        return JsonResponse({"name": field_name}, safe=True)


def delete_google_sheet(request, google_sheet_id):
    GoogleSheet.objects.get(id=google_sheet_id).delete()
    return redirect('importer')

def load_google_sheet(request, google_sheet_id):
    google_sheet = GoogleSheet.objects.get(id=google_sheet_id)
    from_google_sheet(google_sheet.url)

    response_data = {}
    response_data['result'] = 'Loaded sheet successfully!'
    response_data['name'] = google_sheet.name

    return HttpResponse(
        json_module.dumps(response_data),
        content_type="application/json"
    )

def importer(request):
    if request.method == "POST":
        data = {'name': request.POST.get('name'), 'url': request.POST.get('url')}
        form = GoogleSheetForm(data)
        if form.is_valid():
            sheet = form.save()
            return load_google_sheet(request, sheet.id)

    return HttpResponse(
        json_module.dumps({"nothing to see": "this isn't happening"}),
        content_type="application/json"
    )

def get_sheets(request):
    if request.method == "GET":
        sheetObjects = GoogleSheet.objects.all()
        sheets = [sheet.name for sheet in sheetObjects]
        sheetJSON = json_module.dumps(sheets)
        return HttpResponse(sheetJSON)
    return redirect('homepage')

def json(request):
    serializer = ProjectSerializer(Project.objects.all(), many=True)
    return JsonResponse(serializer.data, safe=False)

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

def projektit(request):
    dd = ContentType.objects.get_for_model(DecimalDimension)
    budgets = ProjectDimension.objects.filter(content_type=dd)
    projects_all = Project.objects.all()
    organizations_all = Organization.objects.all()
    return render(request, 'projektit.html', {'projects': projects_all, 'organizations': organizations_all, 'budgets':budgets})

def databaseview(request):
    if request.method == "POST":
       form = CronForm(request.POST)

       if form.is_valid:
          projs = Project.objects.filter(parent=request.POST.get("orgs", ""))

          dimensions = []
          dims = {}

          for p in projs:
              dimensions += ProjectDimension.objects.filter(project=p)

          for dim in dimensions:
              if dim.dimension_object.name not in dims:
                  dims[dim.dimension_object.name] = str(dim).replace("Dimension", "")



          #redirect to the url where you'll process the input
          return render(request, 'droptable_organization.html', {'form':form, 'projs':projs, 'dims':dims, 'dimensions':dimensions}) # insert reverse or url
    else:
         form = CronForm()
    return render(request, 'droptable_organization.html', {'form':form})

def get_orgs(request):
    serializer = OrganizationSerializer(Organization.objects.all(), many=True)
    return JsonResponse(serializer.data, safe=False)
