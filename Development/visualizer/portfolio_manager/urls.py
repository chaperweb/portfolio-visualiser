from django.conf.urls import url
from django.conf import settings


from . import views

urlpatterns = [
    url(r'^upload-new-project$', views.add_new_project, name='add_new_project'),
    url(r'^add_new_org$', views.add_new_org, name='add_new_org'),
    url(r'^projects$', views.projects, name='projects'),
    url(r'^org$', views.organizations, name='select_org'),
    url(r"^projects/(?P<project_id>[0-9]+)$", views.show_project, name='show_project'),
    url(r'^projects/(?P<project_id>[0-9]+)/edit/$', views.project_edit, name='project_edit'),
	  url(r'^load-sheet-data$', views.load_sheet_data, name='add_sheet_data'),
    url(r'^history$', views.history, name='history'),
    url(r"^json/(?P<project_id>[0-9]+)$", views.json, name='json'),
]
