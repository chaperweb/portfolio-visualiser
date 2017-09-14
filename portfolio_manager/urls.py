##
#
# Portfolio Visualizer
#
# Copyright (C) 2017 Codento
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##
from django.conf import settings
from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.contrib.auth.views import login as auth_login, logout as auth_logout

from . import views

#URLs listed as following
#Top view is the leftmost, every functionalities related to that is step right
#Example Homepage is the top(found in navbar)
#Visualizations on the page (path, projectdependencies, 4-field) are step right
ajax_patterns = [
    url(r'^get_sheets$', views.get_sheets, name='get_sheets'),
    url(r'^get_orgs$', views.get_orgs, name='get_orgs'),
    url(r'^get_pers$', views.get_pers, name='get_pers'),
    url(r'^get_proj$', views.get_proj, name='get_proj'),
    url(r'^get_multiple/(?P<field_type>[A-Za-z]+)/(?P<field_id>[0-9]+)$', views.get_multiple, name='get_multiple'),
    url(r'^get/(?P<project_id>[0-9]+)/fields/$', views.get, name="get_projectfields")
]

urlpatterns = [
    url(r'^signup/$', views.signup, name="signup"),
    url(r'^signin/$', auth_login, name="login"),
    url(r'^signout/$', auth_logout, {'next_page': '/signin/'}, name="logout"),
    url(r'^$', views.home, name='homepage'),
        url(r'^path$', TemplateView.as_view(template_name="path.html"), name='path'),
        url(r'^projectdependencies$', TemplateView.as_view(template_name="projectdependencies.html"), name='projectdependencies'),
        url(r'^fourfield$', TemplateView.as_view(template_name="fourfield.html"), name='fourfield'),
    url(r'^projects$', views.projects, name='projects'),
        url(r"^projects/(?P<project_id>[0-9]+)$", views.show_project, name='show_project'),
            url(r'^projects/(?P<project_id>[0-9]+)/edit/(?P<field_type>[A-Za-z]+)$', views.project_edit, name='project_edit'),
    url(r'^manage/admin_tools$', views.admin_tools, name='admin_tools'),
    url(r'^manage/milestone$', views.milestones, name="milestones"),
    url(r"^manage/add_user$", views.add_user, name='add_user'),
        url(r"^importer$", views.importer, name='importer'),
        url(r'^create_org$', views.create_org, name='create_org'),
        url(r'^create_person$', views.create_person, name='create_person'),
    url(r'^database$', views.databaseview, name='databaseview'),
    url(r"^about$", TemplateView.as_view(template_name="about.html"), name='about'),
    url(r'^addproject$', views.addproject, name='addproject'),
    url(r'^add_field$', views.add_field, name='add_field'),
    url(r'^snapshots(/(?P<vis_type>[A-Za-z]+))?(/(?P<snapshot_id>[0-9]+))?$', views.snapshots, name='snapshots'),
    url(r'^create_snapshot$', views.create_snapshot, name='create_snapshot'),
    url(r"^json$", views.json, name='json'),
    url(r'^microsoft_signin/$', views.microsoft_signin, name='microsoft_signin'),
    url(r'^gettoken/$', views.gettoken, name='gettoken'),
    url(r'^excel/$', views.excel, name='excel'),
    url(r'^excel/import$', views.import_excel, name='import_excel'),
    url(r'^excel/export$', views.export_excel, name='export_excel'),
    url(r'^presentations(/(?P<presentation_id>[0-9]+))?$', views.presentation, name="presentations"),
    url(r'^presentations/edit_presentation/(?P<presentation_id>[0-9]+)$', views.edit_presentation, name="edit_presentation"),
    url(r'^presentations/new_presentation$', TemplateView.as_view(template_name="presentations/new_presentation.html"), name='new_presentation'),
    url(r'^presentations/save_presentation(/(?P<presentation_id>[0-9]+))$', views.save_presentation, name='save_presentation'),
    # these are for ajax requests
    url(r'', include(ajax_patterns)),

]
