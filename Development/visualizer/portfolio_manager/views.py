from django.shortcuts import render, redirect
from portfolio_manager.models import Project
from portfolio_manager.forms import ProjectForm
# Create your views here.
# Bujaa
def add_new_project(request):
    if request.method == 'POST':
        form = ProjectForm()
        if form.is_valid():
            project = Project(name = form.cleaned_data['name'])
            #startTime = form.cleaned_data['startTime'],
            #        duration = form.cleaned_data['duration'])
            project.save()
            form = ProjectForm()
        return redirect('projects')

    elif request.method == 'GET':
        form = ProjectForm()
    return render(request, 'uploadproject.html', {'form': form})

def projects(request):
        projects_all = Project.objects.all()

        return render(request, 'projects.html', {'projects': projects_all})
