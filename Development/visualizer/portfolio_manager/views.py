from django.shortcuts import render, redirect, get_object_or_404
from portfolio_manager.models import *
from portfolio_manager.forms import *
from django.contrib.contenttypes.models import ContentType
import logging
from django.http import JsonResponse, HttpResponse, QueryDict
from portfolio_manager.serializers import ProjectSerializer, OrganizationSerializer, PersonSerializer, ProjectNameIdSerializer
from portfolio_manager.importer import from_google_sheet
import json as json_module

# LOGGING
logger = logging.getLogger('django.request')

def home(request):

    # milestones for project sneak peeks (only future milestones, ordered by date)
    milestones = Milestone.objects.filter(due_date__gte = datetime.now()).order_by('due_date')

    # dictionary for (project -> next milestone)
    mils = {}
    for m in milestones:
        if m.project not in mils:
            mils[m.project] = m.due_date

    # dimensions for project manager and end date of project, for project sneak peeks
    dims = ProjectDimension.objects.all()
    assPersonD = ContentType.objects.get_for_model(AssociatedPersonDimension)
    dated = ContentType.objects.get_for_model(DateDimension)
    assPersonDs = dims.filter(content_type=assPersonD)
    dateds = dims.filter(content_type=dated)
    context = {}
    context["projects"] = Project.objects.all()
    context['assPerson'] = assPersonDs
    context["mils"] = mils
    context['dates'] = dateds
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
    # If you want to modify the owning organization
    if field_name == "Organization":
        try:
            org = Organization.objects.get(name=request.POST.get('name'))
        except Organization.DoesNotExist:
            org = Organization(name=request.POST.get('name'))
            org.save()
        proj.parent = org
        proj.save()
        return JsonResponse({"name": request.POST.get('name')})

    # If you want to modify a associated organization
    if field_name == "assorg":
        try:
            org = Organization.objects.get(name=request.POST.get('org'))
            ct = ContentType.objects.get_for_model(AssociatedOrganizationDimension)
            td = ProjectDimension.objects.filter(content_type= ct, project_id=project_id)
            tds = []
            # Manual filtering
            for t in td:
                if t.dimension_object.name == request.POST.get('field'):
                    tds = t.dimension_object
                    break;

            tds.value = org
            tds.save()
            return JsonResponse({"field": tds.name, "value": tds.value.name}, safe=True)

        except Organization.DoesNotExist:
            print("Couldn't find the organization")

    # If you want to modify a text field
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

    # If you want to modify a decimal field
    elif field_name == "decimal":
        ct = ContentType.objects.get_for_model(DecimalDimension)
        td = ProjectDimension.objects.filter(content_type= ct, project_id=project_id)
        tds = []
        # Manual filtering
        for t in td:
            if t.dimension_object.name == request.POST.get('field'):
                tds = t.dimension_object
                break;

        tds.value = request.POST.get('decValue')
        tds.save()
        return JsonResponse({"field": tds.name, "value": tds.value}, safe=True)

    # If you want to modify a single person field
    elif field_name == "person":
        try:
            p = Person.objects.get(pk=request.POST.get('perID'))
            ct = ContentType.objects.get_for_model(AssociatedPersonDimension)
            td = ProjectDimension.objects.filter(content_type= ct, project_id=project_id)
            tds = []
            # Manual filtering
            for t in td:
                if t.dimension_object.name == request.POST.get('field'):
                    tds = t.dimension_object
                    break;

            tds.value = p
            tds.save()
            return JsonResponse({"value": p.first_name + " " + p.last_name, "field": tds.name})
        except Person.DoesNotExist:
            print("Couldn't find the person")

    # If you want to modify a date field
    elif field_name == "date":
        ct = ContentType.objects.get_for_model(DateDimension)
        td = ProjectDimension.objects.filter(content_type= ct, project_id=project_id)
        tds = []
        # Manual filtering
        for t in td:
            if t.dimension_object.name == request.POST.get('field'):
                tds = t.dimension_object
                break;

        tds.update_date(request.POST.get('date'))
        tds.save()
        return JsonResponse({"field": tds.name, "value": tds.value}, safe=True)

    else:
        return JsonResponse({"name": field_name, 'error': "No field matched"}, safe=True)

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

#   Import google sheet
#   Doesn't return anything if it isn't a POST to trigger the ajax error function
def importer(request):
    if request.method == "POST":
        data = {'name': request.POST.get('name'), 'url': request.POST.get('url')}
        form = GoogleSheetForm(data)
        if form.is_valid():
            sheet = form.save()
            return load_google_sheet(request, sheet.id)

#   Gets all previously uploaded sheets and returns them in JSON
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


 # site to see all projects, grouped by organization

def projects(request):
    dd = ContentType.objects.get_for_model(DecimalDimension)
    budgets = ProjectDimension.objects.filter(content_type=dd)
    projects_all = Project.objects.all()
    organizations_all = Organization.objects.all()
    return render(request, 'projects.html', {'projects': projects_all, 'organizations': organizations_all, 'budgets':budgets})

# site to show datafields by organization
def databaseview(request):
    if request.method == "POST":
       form = OrgForm(request.POST)

       if form.is_valid:
          projs = Project.objects.filter(parent=request.POST.get("orgs", ""))

        #   all dimensions in every project of the organization
          dimensions = []
          for p in projs:
              dimensions += ProjectDimension.objects.filter(project=p)

        # (dimension name -> datatype) dictionary
          dims = {}
          for dim in dimensions:
              if dim.dimension_object.name not in dims:
                  dims[dim.dimension_object.name] = str(dim).replace("Dimension", "")

          #redirect to the url where you'll process the input
          return render(request, 'database.html', {'form':form, 'projs':projs, 'dims':dims})
    else:
         form = OrgForm()
    return render(request, 'database.html', {'form':form})

# Gets all organizations and return them in a JSON string
def get_orgs(request):
    serializer = OrganizationSerializer(Organization.objects.all(), many=True)
    return JsonResponse(serializer.data, safe=False)

# Gets all persons and return them in a JSON string
def get_pers(request):
    serializer = PersonSerializer(Person.objects.all(), many=True)
    return JsonResponse(serializer.data, safe=False)

# Gets all projects and returns them with name and id in a JSON
def get_proj(request):
    serializer = ProjectNameIdSerializer(Project.objects.all(), many=True)
    return JsonResponse(serializer.data, safe=False)

#   Function that gets the multiple entries in a dimension that has multiple
#   items.
#   Input:
#       A request
#       The id of the project you want to search for
#       The type of dimension, e.g. assperson( AssociatedPersonsDimension )
#       The name of the field, e.g. Members
#   Output:
#       A JSON string that has the names of the searched for items

#   As this function is only to be called with ajax a else statement has
#   purposefully been left out to trigger the errorfunction in the ajax call

def get_multiple(request, project_id, type, field_name):
    # Get the project
    theProject = get_object_or_404(Project, pk=project_id)
    # If AssociatedPersonsDimension
    if type == "asspersons":
        # ContentType
        assPersonsD = ContentType.objects.get_for_model(AssociatedPersonsDimension)
        # The dimensions of correct content_type and for the correct project_id
        assPersonsDs = ProjectDimension.objects.filter(content_type=assPersonsD, project_id=theProject.id)
        persons = []
        personsList = []
        # Loop through the dimensions
        for dim in assPersonsDs:
            # Get the dimension object
            dimO = dim.dimension_object
            if dimO.name == field_name:
                for pers in dimO.persons.all():
                    persons.append(pers)
        for p in persons:
            personsList.append({'id':p.pk, 'name': p.first_name + " " + p.last_name})
        return JsonResponse({'type': 'persons', 'items': personsList})

    # If AssociatedProjectsDimension
    elif type == "assprojects":
        # ContentType
        assProjsD = ContentType.objects.get_for_model(AssociatedProjectsDimension)
        # The dimensions of correct content_type and for the correct project_id
        assProjsDs = ProjectDimension.objects.filter(content_type=assProjsD, project_id=theProject.id)
        projects = []
        projectList = []
        # Loop through the dimensions
        for dim in assProjsDs:
            # Get the dimension object
            dimO = dim.dimension_object
            if dimO.name == field_name:
                for proj in dimO.projects.all():
                    projects.append(proj)
        for p in projects:
            projectList.append({'id': p.id, 'name': p.name})
        return JsonResponse({'type': 'projects', 'items': projectList})

def remove_person_from_project(request):
    if request.is_ajax() and request.method == "PATCH":
        qdict = QueryDict(request.body)
        pid = qdict.get('id')
        person = Person.objects.get(pk=pid)
        ct = ContentType.objects.get_for_model(AssociatedPersonsDimension)
        dim = ProjectDimension.objects.get(content_type=ct, project_id=qdict.get('project_id'))
        dim.dimension_object.persons.remove(person)
        return JsonResponse({"result": True, "id": pid})

def remove_project_from_project(request):
    if request.is_ajax() and request.method == "PATCH":
        qdict = QueryDict(request.body)
        pid = qdict.get('id')
        project = Project.objects.get(pk=pid)
        ct = ContentType.objects.get_for_model(AssociatedProjectsDimension)
        dim = ProjectDimension.objects.get(content_type=ct, project_id=qdict.get('project_id'))
        dim.dimension_object.projects.remove(project)
        return JsonResponse({"result": True, "id": pid})

def add_person_to_project(request):
    if request.is_ajax() and request.method == "POST":
        projectID = request.POST.get('projectID')
        personID = request.POST.get('personID')
        project = Project.objects.get(pk=projectID)
        person = Person.objects.get(pk=personID)
        ct = ContentType.objects.get_for_model(AssociatedPersonsDimension)
        dim = ProjectDimension.objects.get(content_type=ct, project_id=projectID)
        dim.dimension_object.persons.add(person)
        return JsonResponse({'result': True, 'id': person.pk, 'name': person.first_name + " " + person.last_name})

def add_project_to_project(request):
    if request.is_ajax() and request.method == "POST":
        toBeAddedID = request.POST.get('toBeAddedID')
        destID = request.POST.get('destID')
        TBAProject = Project.objects.get(pk=toBeAddedID)
        destProject = Project.objects.get(pk=destID)
        ct = ContentType.objects.get_for_model(AssociatedProjectsDimension)
        dim = ProjectDimension.objects.get(content_type=ct, project_id=destID)
        dim.dimension_object.projects.add(TBAProject)
        return JsonResponse({'result': True, 'id': TBAProject.pk, 'name': TBAProject.name})
