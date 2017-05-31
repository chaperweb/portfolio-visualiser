from django.shortcuts import render, redirect, get_object_or_404
from portfolio_manager.models import *
from portfolio_manager.forms import *
from django.contrib.contenttypes.models import ContentType
import django.forms
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
    # Loop through the milestones
    for m in milestones:
        # Checks if m.project is already in the dictionary for next milestone
        if m.project not in mils:
            mils[m.project] = m.due_date

    # dimensions for project manager and end date of project, for project sneak peeks
    dims = ProjectDimension.objects.all()
    # ContentType
    assPersonD = ContentType.objects.get_for_model(AssociatedPersonDimension)
    dated = ContentType.objects.get_for_model(DateDimension)
    # Get dimensions of correct content_type for assPersonDs and dateds
    assPersonDs = dims.filter(content_type=assPersonD)
    dateds = dims.filter(content_type=dated)
    context = {}
    context["projects"] = Project.objects.all()
    context["pre_add_project_form"] = AddProjectForm()
    context['assPerson'] = assPersonDs
    context["mils"] = mils
    context['dates'] = dateds
    return render(request, 'homepage.html', context)

def admin_tools(request):
    form = AddProjectForm()
    form.fields['name'].widget.attrs['class'] = 'form-control'
    form.fields['organization'].widget.attrs['class'] = 'form-control'
    return render(request, 'admin_tools.html', {'pre_add_project_form': form})

# Site to add a new organization
def add_new_org(request):
    if request.method == 'POST':
        data = {'name': request.POST.get('orgName')}
        form = OrganizationForm(data)
        if form.is_valid():
            # Save a new Organization
            organization = Organization(name = form.cleaned_data['name'])
            organization.save()

            template = ProjectTemplate()
            template.name = 'default'
            template.organization = organization
            template.save()

            template_dimension = ProjectTemplateDimension()
            template_dimension.template = template
            template_dimension.name = 'SizeMoney'
            template_dimension.content_type = ContentType.objects.get_for_model(DecimalDimension)
            template_dimension.save()

            template_dimension = ProjectTemplateDimension()
            template_dimension.template = template
            template_dimension.name = 'EndDate'
            template_dimension.content_type = ContentType.objects.get_for_model(DateDimension)
            template_dimension.save()

            template_dimension = ProjectTemplateDimension()
            template_dimension.template = template
            template_dimension.name = 'ProjectManager'
            template_dimension.content_type = ContentType.objects.get_for_model(AssociatedPersonDimension)
            template_dimension.save()



            # Response for the addition of an organization
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
            # Save a new person
            person = Person(first_name=form.cleaned_data['first'], last_name=form.cleaned_data['last'])
            person.save()
            # Response for the addition of a person
            response_data = {}
            response_data['result'] = 'Created person successfully!'
            response_data['name'] = person.first_name + " " + person.last_name
            return HttpResponse(
                json_module.dumps(response_data),
                content_type="application/json"
            )

# Function to add field
def add_field(request):
    if request.method == "POST":
        try:
            form = ProjectTemplateForm(request.POST)
            org = Organization.objects.get(name=request.POST['organization'])
            template = ProjectTemplate.objects.get(organization=org)
            ct = ContentType.objects.get_for_id(request.POST['field_type'])
            template_dim = ProjectTemplateDimension(name=request.POST['name'], template=template, content_type=ct)
            template_dim.save()

            add_field_form = ProjectTemplateForm(initial={'organization': request.POST['organization'] })
            orgform = OrgForm({'orgs': org})
            # (dimension name -> datatype) dictionary
            dims = {}
            templates = org.templates.all()
            if len(templates) > 0:
                template = templates[0]
                for template_dimension in template.dimensions.all():
                    #TODO: group them by types to make the site easier to view?
                    dims[template_dimension.name] = str(template_dimension.content_type.model_class().__name__).replace("Dimension", "")

            resultmsg = "Successfully added the \"%s\"-field" % request.POST['name']
            return render(request, 'database.html', {'form':orgform, 'dims':dims, 'add_field_form': add_field_form, 'add_field_success': resultmsg})
        except:
            orgform = OrgForm()
            add_field_form = ProjectTemplateForm()
            resultmsg = "An error occured"
            return render(request, 'database.html', {'form': orgform, 'add_field_form': add_field_form, 'add_field_fail': resultmsg})

def show_project(request, project_id):
        theProject = get_object_or_404(Project, pk=project_id)
        # ContentTypes
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

        # for organization history
        history_all = theProject.history.all().order_by('-history_date')[:5]

        orgs = {}
        for h in history_all:
            orgs[h.history_date] = h.parent

        context['orghistory'] = sorted(orgs.items(), reverse=True)


        return render(request, 'project.html', context)

# Site for editing a project
def project_edit(request, project_id, field_name):
    proj = get_object_or_404(Project, pk=project_id)
    # If you want to modify the owning organization
    if field_name == "Organization":
        try:
            # Existing organizations
            org = Organization.objects.get(name=request.POST.get('name'))
        except Organization.DoesNotExist:
            # Saves new organization
            org = Organization(name=request.POST.get('name'))
            org.save()
        # Saves the modified owner of the project
        proj.parent = org
        proj.save()
        return JsonResponse({"name": request.POST.get('name')})

    # If you want to modify a associated organization
    if field_name == "assorg":
        try:
            # Existing organizations
            org = Organization.objects.get(name=request.POST.get('org'))
            # ContentType
            ct = ContentType.objects.get_for_model(AssociatedOrganizationDimension)
            # The dimensions of correct content_type and correct project_id
            td = ProjectDimension.objects.filter(content_type= ct, project_id=project_id)
            tds = []
            # Manual filtering
            for t in td:
                if t.dimension_object.name == request.POST.get('field'):
                    tds = t.dimension_object
                    break;
            # Saves modified associated organization
            tds.value = org
            tds.save()
            return JsonResponse({"field": tds.name, "value": tds.value.name}, safe=True)

        except Organization.DoesNotExist:
            print("Couldn't find the organization")

    # If you want to modify a text field
    elif field_name == "text":
        # ContentType
        ct = ContentType.objects.get_for_model(TextDimension)
        # The dimensions of correct content_type and correct project_id
        td = ProjectDimension.objects.filter(content_type= ct, project_id=project_id)
        tds = []
        # Manual filtering
        for t in td:
            if t.dimension_object.name == request.POST.get('field'):
                tds = t.dimension_object
                break;
        # Saves the modified Text field
        tds.value = request.POST.get('textValue')
        tds.save()
        return JsonResponse({"field": tds.name, "value": tds.value}, safe=True)

    # If you want to modify a decimal field
    elif field_name == "decimal":
        # ContentType
        ct = ContentType.objects.get_for_model(DecimalDimension)
        # The dimensions of correct content_type and correct project_id
        td = ProjectDimension.objects.filter(content_type= ct, project_id=project_id)
        tds = []
        # Manual filtering
        for t in td:
            if t.dimension_object.name == request.POST.get('field'):
                tds = t.dimension_object
                break;
        # Saves the modified decimal field
        tds.value = request.POST.get('decValue')
        tds.save()
        return JsonResponse({"field": tds.name, "value": tds.value}, safe=True)

    # If you want to modify a single person field
    elif field_name == "person":
        try:
            # Existing persons
            p = Person.objects.get(pk=request.POST.get('perID'))
            # ContentType
            ct = ContentType.objects.get_for_model(AssociatedPersonDimension)
            # The dimensions of correct content_type and correct project_id
            td = ProjectDimension.objects.filter(content_type= ct, project_id=project_id)
            tds = []
            # Manual filtering
            for t in td:
                if t.dimension_object.name == request.POST.get('field'):
                    tds = t.dimension_object
                    break;
            # Saves the modified single person field
            tds.value = p
            tds.save()
            return JsonResponse({"value": p.first_name + " " + p.last_name, "field": tds.name})
        except Person.DoesNotExist:
            print("Couldn't find the person")

    # If you want to modify a date field
    elif field_name == "date":
        # ContentType
        ct = ContentType.objects.get_for_model(DateDimension)
        # The dimensions of correct content_type and correct project_id
        td = ProjectDimension.objects.filter(content_type= ct, project_id=project_id)
        tds = []
        # Manual filtering
        for t in td:
            if t.dimension_object.name == request.POST.get('field'):
                tds = t.dimension_object
                break;
        # Updates and saves the date field
        tds.update_date(request.POST.get('date'))
        tds.save()
        return JsonResponse({"field": tds.name, "value": tds.value}, safe=True)

    else:
        return JsonResponse({"name": field_name, 'error': "No field matched"}, safe=True)

#   Import google sheet
#   Doesn't return anything if it isn't a POST or a DELETE to trigger the ajax error function
def importer(request):
    if request.method == "POST":
        data = {'name': request.POST.get('name'), 'url': request.POST.get('url')}
        form = GoogleSheetForm(data)
        if form.is_valid():
            sheet = form.save()
            # Load the google sheet
            google_sheet = GoogleSheet.objects.get(id=sheet.id)
            from_google_sheet(google_sheet.url)

            response_data = {}
            response_data['result'] = 'Loaded sheet successfully!'
            response_data['name'] = google_sheet.name

            return HttpResponse(
                json_module.dumps(response_data),
                content_type="application/json"
            )
    elif request.method == "DELETE":
        GoogleSheet.objects.get(id=request.DELETE['sheet_id']).delete()
        response_data = {}
        response_data['result'] = 'Deleted sheet successfully!'
        return HttpResponse(
            json_module.dumps(response_data),
            content_type="application/json"
        )

#   Gets all previously uploaded sheets and returns them in JSON
def get_sheets(request):
    if request.method == "GET":
        sheetObjects = GoogleSheet.objects.all()

        sheetsurls = []
        for s in sheetObjects:
            sheetsurls.append(s.name)
            sheetsurls.append(s.url)
        sheetJSON = json_module.dumps(sheetsurls)
        return HttpResponse(sheetJSON)
    return redirect('homepage')

def json(request):
    serializer = ProjectSerializer(Project.objects.all(), many=True)
    return JsonResponse(serializer.data, safe=False)

 # site to see all projects, grouped by organization
def projects(request):
    # ContentType
    dd = ContentType.objects.get_for_model(DecimalDimension)
    # The dimensions of correct content_type
    budgets = ProjectDimension.objects.filter(content_type=dd)
    # Existing projects
    projects_all = Project.objects.all()
    # Existing organizations
    organizations_all = Organization.objects.all()
    return render(request, 'projects.html', {'projects': projects_all, 'organizations': organizations_all, 'budgets':budgets})

# site to show datafields by organization
def databaseview(request):
    if request.method == "POST":
        form = OrgForm(request.POST)

        if form.is_valid:
            add_field_form = ProjectTemplateForm(initial={'organization': request.POST['orgs'] })
            # (dimension name -> datatype) dictionary
            dims = {}
            organization = Organization.objects.get(name=request.POST['orgs'])
            templates = organization.templates.all()
            if len(templates) > 0:
                template = templates[0]
                for template_dimension in template.dimensions.all():
                    #TODO: group them by types to make the site easier to view?
                    dims[template_dimension.name] = str(template_dimension.content_type.model_class().__name__).replace("Dimension", "")
            #redirect to the url where you'll process the input
            return render(request, 'database.html', {'form':form, 'dims':dims, 'add_field_form': add_field_form})
    else:
        add_field_form = ProjectTemplateForm()
        form = OrgForm()
    return render(request, 'database.html', {'form':form, 'add_field_form': add_field_form})

def addproject(request):

    add_project_form = None
    add_project_form_prefix = 'add_project_form'
    if request.POST:
        add_project_form = AddProjectForm(request.POST, prefix=add_project_form_prefix)
    else:
        # Get initial values from referrering page that asked for project name and organization
        add_project_form = AddProjectForm(prefix='add_project_form', initial={'name': request.GET.get('name'), 'parent': request.GET.get('organization', ''), 'organization': request.GET.get('organization', '')})

    # Prevent user from chaning name or organization on "Add project" page.
    # If it were possible to change organization, every time organization selection is changed
    # organization project template must be reloaded to the page. Also the name field of project
    # instance should match the value of TextDimension with name 'Name'. Simpler implementation
    # when user is not allowed to change these values.
    add_project_form.disable_name_and_organization()

    forms = [add_project_form]

    try:
        organization = Organization.objects.get(pk=request.GET.get('organization', add_project_form.data.get(add_project_form_prefix+'-parent')))
        templates = organization.templates.all()
        if len(templates) > 0:
            template = templates[0]
            for template_dimension in template.dimensions.all():
                template_dimension_form_class = globals()[template_dimension.content_type.model_class().__name__+"Form"]
                # TODO: Should we check more carefully what is drawn from globals(). Security issue?
                template_dimension_form = None
                if request.POST:
                    template_dimension_form = template_dimension_form_class(request.POST, dimension_name=template_dimension.name, project_form=add_project_form, prefix=str(template_dimension.id)+'_form')
                else:
                    template_dimension_form = template_dimension_form_class(dimension_name=template_dimension.name, project_form=add_project_form, prefix=str(template_dimension.id)+'_form')
                    if template_dimension.name == 'Name':
                        template_dimension_form.fields['value'].widget = django.forms.HiddenInput()
                        template_dimension_form.fields['value'].initial = request.GET.get('name')
                forms.append(template_dimension_form)

    except Organization.DoesNotExist:
        pass

    forms_valid = True
    if request.POST:
        for form in forms:
            if form.is_valid():
                continue
            else:
                forms_valid = False

        if forms_valid:
            for form in forms:
               form.save()
            return redirect('show_project', add_project_form.instance.id)

    return render(request, 'add_project.html', {'forms': forms })

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

#   As this function is only to be called with ajax an else statement has
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


def create_pathsnapshot(name, description, project_id, x, y):
    p_snap = PathSnapshot()
    project = Project.objects.get(pk=project_id)
    p_snap.name = name
    p_snap.description = description
    p_snap.snap_type = 'PA'
    p_snap.project = project
    p_snap.dimension_object_x = x
    p_snap.dimension_object_y = y
    p_snap.save()
    return p_snap


def create_fourfieldsnapshot(request):
    pass


def snapshots(request, vis_type, snapshot_id):
    response_data = {}
    template = 'snapshots/error.html'

    #   Show all snapshots
    if not vis_type and not snapshot_id:
        snaps = []
        snap_types = Snapshot.get_subclasses()
        for snap_type in snap_types:
            snaps.extend(snap_type.objects.all())
        response_data = {
            'snaps': snaps
        }
        template = 'snapshots/multiple/all.html'

    #   Show all snapshots of vis_type
    elif vis_type and not snapshot_id:
        if vis_type == 'path':
            snaps = PathSnapshot.objects.all()
            template = 'snapshots/multiple/path.html'
        elif vis_type == 'fourfield':
            snaps = FourFieldSnapshot.objects.all()
            template = 'snapshots/multiple/fourfield.html'

        response_data = {
            'snaps': snaps
        }

    #   Show a single snapshot
    elif vis_type and snapshot_id:
        try:
            if vis_type == 'path':
                snap = PathSnapshot.objects.get(pk=snapshot_id)
                name = snap.name
                desc = snap.description
                proj = snap.project.name
                x = snap.dimension_object_x.name
                y = snap.dimension_object_y.name
                response_data = {
                    'name': name,
                    'description': desc,
                    'project': proj,
                    'x': x,
                    'y': y
                }
                template = 'snapshots/single/path.html'
            elif vis_type == 'fourfield':
                snap = FourFieldSnapshot.objects.get(pk=snapshot_id)
                name = snap.name
                desc = snap.description
                x = snap.x_dimension.name
                y = snap.y_dimension.name
                radius = snap.radius_dimension.name
                start_date = snap.start_date
                end_date = snap.end_date
                zoom = snap.zoom
                response_data = {
                    'name': name,
                    'description': desc,
                    'x': x,
                    'y': y,
                    'radius': radius,
                    'start_date': start_date,
                    'end_date': end_date,
                    'zoom': zoom
                }
                template = 'snapshots/single/fourfield.html'
        except Exception as e:
            pass

    #   Render the appropriate template
    return render(request, template, response_data)


def create_snapshot(request):
    if request.method == 'POST':
        snapshot_type = request.POST['type']
        if snapshot_type == 'path':
            x_proj_template = ProjectDimension.objects.get(pk=request.POST['x_dim'])
            y_proj_template = ProjectDimension.objects.get(pk=request.POST['y_dim'])

            name = request.POST['name']
            description = request.POST['description']
            pid = request.POST['project_id']
            x_dim = x_proj_template.dimension_object
            y_dim = y_proj_template.dimension_object

            p_snap = create_pathsnapshot(
                        name=name,
                        description=description,
                        project_id=pid,
                        x=x_dim,
                        y=y_dim
                    )
            url = 'snapshots/path/{}'.format(p_snap.id)
            return redirect(url, permanent=True)
        elif snapshot_type == 'fourfield':
            create_fourfieldsnapshot(request)
        else:
            pass
