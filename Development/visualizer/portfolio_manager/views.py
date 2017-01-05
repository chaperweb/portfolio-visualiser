from django.shortcuts import render, redirect, get_object_or_404
from portfolio_manager.models import Project,Organization
from portfolio_manager.forms import ProjectForm,OrganizationForm,CronForm
# Create your views here.
# Bujaa
def add_new_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            organization = Organization(name = form.cleaned_data['parent'])
            organization.save()

            newproject = Project(name = form.cleaned_data['name'], parent = organization)

        #    newproject = organization.project_set.create(name=form.cleaned_data['name'])
            newproject.save()
            print(newproject.name)

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

# def organizations(request):
    # project = Project.objects.all()
    # oform = request.POST
    # if request.method =='POST':
    #     print(oform['organizationID'])
    #     selected_item = get_object_or_404(Project, organization=oform)
    #     return redirect('projects')
#    orgs = Organization.objects.all()
    #if request.method == 'POST':
    #    form = OrganizationForm(request.POST)
    #    if form.is_valid():
    #        projects = Project.objects.filter(parent = selected_item)
    #        return redirect('projects')
    #return render(request, 'droptable_organization.html', {'orgs':orgs})

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


def show_project(request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        return render(request, 'project.html', {'project': project })

def project_edit(request, project_id):
    proj = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = ProjectForm(request.POST)

        if form.is_valid():

            # proj = form.save(commit=False)
            proj.name = form.cleaned_data['name']
            proj.parent = form.cleaned_data['parent']
            # print("org: " + organization)
            proj.save()
        return redirect('show_project', project_id=proj.pk)
    else:
        data = {
    'name': proj.name,
    'parent': proj.parent
}
        form = ProjectForm(data)
    return render(request, 'project_edit.html', {'form': form})
