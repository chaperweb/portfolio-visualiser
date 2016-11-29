from django.shortcuts import render

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
        form = ImageForm()
    return render(request, 'uploadform.html', {'form': form})
