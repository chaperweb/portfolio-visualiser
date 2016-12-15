from django.shortcuts import render, redirect, get_object_or_404
from portfolio_manager.models import Project,Organization
from portfolio_manager.forms import ProjectForm,OrganizationForm,CronForm
import logging
# Create your views here.

# LOGGING
logger = logging.getLogger('django.request')


# Bujaa
def add_new_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            organization = Organization(name = form.cleaned_data['organization'])
            organization.save()

            newproject = Project(name = form.cleaned_data['name'], parent = organization)

            newproject.save()
            logger.info("Project added: " + newproject.name + ", Org: " + newproject.parent.name)

            form = ProjectForm()
        return redirect('projects')

    elif request.method == 'GET':
        form = ProjectForm()
    return render(request, 'uploadproject.html', {'form': form})

def projects(request):
    projects_all = Project.objects.all()
    return render(request, 'projects.html', {'projects': projects_all})

def organizations(request):

   if request.method == "POST":
      form = CronForm(request.POST)

      if form.is_valid:
         print(request.POST.get("orgs", ""))

         projs = Project.objects.filter(parent=request.POST.get("orgs", ""))

         #redirect to the url where you'll process the input
         return render(request, 'projects_by_organization.html', {'projs':projs}) # insert reverse or url
   else:
        form = CronForm()
   return render(request, 'droptable_organization.html', {'form':form})
