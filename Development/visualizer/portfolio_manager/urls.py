from django.conf.urls import url
from django.conf import settings


from . import views

urlpatterns = [
    url(r'^upload-new-project$', views.add_new_project, name='add_new_project'),
     url(r'^projects$', views.projects, name='projects'),
     url(r'^org$', views.organizations, name='select_org')
]
