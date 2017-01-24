from django.shortcuts import render, redirect, get_object_or_404
from portfolio_manager.models import Project,Organization
from portfolio_manager.forms import ProjectForm,OrganizationForm,CronForm,SheetUrlForm
import portfolio_manager.scripts.load_data
import logging
from django.http import JsonResponse
from serializers import ProjectSerializer

# LOGGING
logger = logging.getLogger('django.request')

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

def add_new_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            # Save a new Organization
            organization = Organization(name = form.cleaned_data['parent'])
            organization.save()

            # Save a new Project
            newproject = Project(name = form.cleaned_data['name'], parent = organization)
            newproject.save()

            form = ProjectForm()
        return redirect('projects')

    elif request.method == 'GET':
        form = ProjectForm()
    return render(request, 'uploadproject.html', {'form': form})

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

def projects(request):
    projects_all = Project.objects.all()
    return render(request, 'projects.html', {'projects': projects_all})

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
        project = get_object_or_404(Project, pk=project_id)
        return render(request, 'project.html', {'project': project })

def project_edit(request, project_id):
    proj = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():
            # Update the projects info
            proj.name = form.cleaned_data['name']
            proj.parent = form.cleaned_data['parent']
            proj.save()

        return redirect('show_project', project_id=proj.pk)
    else:
        data = {
    'name': proj.name,
    'parent': proj.parent
}
        form = ProjectForm(data)
    return render(request, 'project_edit.html', {'form': form})
	
def load_sheet_data(form):
	if request.method == "POST":
		form = SheetUrlForm(request.POST)
		
		if form.is_valid():
		  portfolio_manager.scripts.load_data.load_data_from_url(form.cleaned_data['url'])
		  return redirect('load-sheet-data')

def json(request, project_id):
    project = Project.objects.get(pk=project_id)
    serializer = ProjectSerializer(project)
    return JsonResponse(serializer.data)

