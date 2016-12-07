from django.conf.urls import url
from django.conf import settings


from . import views

urlpatterns = [
    url(r'^upload-new-project$', views.add_new_project, name='add_new_project'),
     url(r'^projects$', views.projects, name='projects'),
     url(r'^org$', views.organizations, name='select_org'),
      url(r"^projects/(?P<project_id>[0-9]+)$", views.show_project, name='show_project'),
       url(r'^projects/(?P<project_id>[0-9]+)/edit/$', views.project_edit, name='project_edit'),
]
