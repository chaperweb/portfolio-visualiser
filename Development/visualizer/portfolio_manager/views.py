from django.shortcuts import render, redirect, get_object_or_404
from portfolio_manager.models import Project,Organization
from portfolio_manager.forms import ProjectForm
# Create your views here.
# Bujaa
def add_new_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            organization = Organization(name = form.cleaned_data['organization'])
            organization.save()

            project = Project(name = form.cleaned_data['name'], parent = organization)
            project.save()

            #startTime = form.cleaned_data['startTime'],
            #        duration = form.cleaned_data['duration'])

            form = ProjectForm()
        return redirect('projects')

    elif request.method == 'GET':
        form = ProjectForm()
    return render(request, 'uploadproject.html', {'form': form})

def projects(request):
    projects_all = Project.objects.all()
    return render(request, 'projects.html', {'projects': projects_all})

def organizations(request):
    project = Project.objects.all()
    oform = request.POST
    if request.method =='POST':
        print(oform['organizationID'])
        selected_item = get_object_or_404(Project, organization=oform)
        return redirect('projects')
    return render(request, 'droptable_organization.html', {'projects': project})
