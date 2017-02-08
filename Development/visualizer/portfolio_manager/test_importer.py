from django.test import TestCase
from models import *
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import *
from serializers import ProjectSerializer
from rest_framework.renderers import JSONRenderer
from importer import from_data_array
from dateutil.parser import parse

class ModelsTestCase(TestCase):

    def setUp(self):
        pass

    def test_import_dimension_name(self):
        data = [[u'id', u'__history_date', u'Name'],
                [u'1', '2013-03-16T17:41:28+00:00', 'foo'],
                ]
        from_data_array(data)
        self.assertEqual('Name', Project.objects.get(id=1).dimensions.all()[0].dimension_object.name)
     
    def test_import_name(self):
        data = [[u'id', u'__history_date', u'Name'],
                [u'1', '2013-03-16T17:41:28+00:00', 'foo'],
                [u'1', '2013-03-17T17:41:28+00:00'],
                [u'1', '2013-03-18T17:41:28+00:00', 'baz'],
                [u'2', '2013-03-20T17:41:28+00:00', 'dir'],
                [u'2', '2013-03-19T17:41:28+00:00', 'biz']
                ]
        from_data_array(data)
        self.assertEqual(2, Project.objects.all().count())
        self.assertEqual(2, Project.objects.get(id=1).dimensions.all()[0].dimension_object.history.all().count())
        self.assertEqual(2, Project.objects.get(id=2).dimensions.all()[0].dimension_object.history.all().count())
        self.assertEqual('dir', Project.objects.get(id=2).dimensions.all()[0].dimension_object.history.all()[0].value)
        self.assertEqual('biz', Project.objects.get(id=2).dimensions.all()[0].dimension_object.history.all()[1].value)

    def test_import_dmy_startdate_dmy_history_date(self):
        data = [[u'id', u'__history_date', u'StartDate'],
                [u'1', '03/18/2013', '5/6/2017'],
                [u'1', '03/16/2013', '3/4/2015']
                ]
        from_data_array(data)
        self.assertEqual(2, Project.objects.get(id=1).dimensions.all()[0].dimension_object.history.all().count())
        self.assertEqual(parse('5/6/2017').replace(tzinfo=pytz.utc), Project.objects.get(id=1).dimensions.all()[0].dimension_object.history.all()[0].value)
        self.assertEqual(parse('3/4/2015').replace(tzinfo=pytz.utc), Project.objects.get(id=1).dimensions.all()[0].dimension_object.history.all()[1].value)

    def test_import_startdate(self):
        data = [[u'id', u'__history_date', u'StartDate'],
                [u'1', '2013-03-16T17:41:28+00:00', '2013-05-16T17:41:28+00:00'],
                [u'1', '2013-03-18T17:41:28+00:00', '2013-07-16T17:41:28+00:00'],
                ]
        from_data_array(data)
        self.assertEqual(1, Project.objects.all().count())
        self.assertEqual(2, Project.objects.get(id=1).dimensions.all()[0].dimension_object.history.all().count())
        self.assertEqual(parse('2013-07-16T17:41:28+00:00'), Project.objects.get(id=1).dimensions.all()[0].dimension_object.history.all()[0].value)
        self.assertEqual(parse('2013-05-16T17:41:28+00:00'), Project.objects.get(id=1).dimensions.all()[0].dimension_object.history.all()[1].value)

    def test_import_projectmanager(self):
        data = [[u'id', u'__history_date', u'ProjectManager'],
                [u'1', '2013-03-16T17:41:28+00:00', 'Pekka'],
                [u'1', '2013-03-18T17:41:28+00:00', 'Matti'],
                [u'1', '2013-03-19T17:41:28+00:00', 'Pekka'],
                ]
        from_data_array(data)
        self.assertEqual(1, Project.objects.all().count())
        self.assertEqual(3, Project.objects.get(id=1).dimensions.all()[0].dimension_object.history.all().count())
        self.assertEqual(2, Person.objects.all().count())
        self.assertEqual(Person.objects.get(first_name='Pekka'), Project.objects.get(id=1).dimensions.all()[0].dimension_object.history.all()[0].value)
        self.assertEqual(Person.objects.get(first_name='Matti'), Project.objects.get(id=1).dimensions.all()[0].dimension_object.history.all()[1].value)
        self.assertEqual(Person.objects.get(first_name='Pekka'), Project.objects.get(id=1).dimensions.all()[0].dimension_object.history.all()[2].value)

    def test_import_members(self):
        data = [[u'id', u'__history_date', u'Members'],
                [u'1', '2013-03-16T17:41:28+00:00', 'Pekka,Matti'],
                [u'1', '2013-03-18T17:41:28+00:00', 'Matti'],
                [u'1', '2013-03-19T17:41:28+00:00', 'Taneli,Pekka'],
                ]
        from_data_array(data)
        self.assertEqual(1, Project.objects.all().count())
        self.assertEqual(3, Person.objects.all().count())
        self.assertEqual(Person.objects.get(first_name='Taneli'), Project.objects.get(id=1).dimensions.all()[0].dimension_object.persons.all()[1])
        self.assertEqual(Person.objects.get(first_name='Pekka'), Project.objects.get(id=1).dimensions.all()[0].dimension_object.persons.all()[0])

    def test_import_projectdependencies(self):
        data = [[u'id', u'__history_date', u'ProjectDependencies'],
                [u'1', '2013-03-16T17:41:28+00:00'],
                [u'2', '2013-03-18T17:41:28+00:00', '1'],
                [u'3', '2013-03-19T17:41:28+00:00', '1,2'],
                ]
        from_data_array(data)
        self.assertEqual(3, Project.objects.all().count())
        self.assertEquals(0, Project.objects.get(id=1).dimensions.all().count())
        self.assertEquals(1, Project.objects.get(id=2).dimensions.all()[0].dimension_object.projects.all().count())
        self.assertEquals(Project.objects.get(pk=1), Project.objects.get(id=2).dimensions.all()[0].dimension_object.projects.all()[0])
        self.assertEquals(2, Project.objects.get(id=3).dimensions.all()[0].dimension_object.projects.all().count())
        self.assertEquals(Project.objects.get(pk=1), Project.objects.get(id=3).dimensions.all()[0].dimension_object.projects.all()[0])
        self.assertEquals(Project.objects.get(pk=2), Project.objects.get(id=3).dimensions.all()[0].dimension_object.projects.all()[1])

    def test_import_owningorganization(self):
        data = [[u'id', u'__history_date', u'OwningOrganization'],
                [u'1', '2013-03-16T17:41:28+00:00', 'Org1'],
                [u'1', '2013-03-18T17:41:28+00:00', 'Org2'],
                [u'1', '2013-03-19T17:41:28+00:00', 'Org1'],
                ]
        from_data_array(data)
        self.assertEqual(1, Project.objects.all().count())
        self.assertEqual(3, Project.objects.get(id=1).dimensions.all()[0].dimension_object.history.all().count())
        self.assertEqual(2, Organization.objects.all().count())
        self.assertEqual(Organization.objects.get(name='Org1'), Project.objects.get(id=1).dimensions.all()[0].dimension_object.history.all()[0].value)
        self.assertEqual(Organization.objects.get(name='Org2'), Project.objects.get(id=1).dimensions.all()[0].dimension_object.history.all()[1].value)
        self.assertEqual(Organization.objects.get(name='Org1'), Project.objects.get(id=1).dimensions.all()[0].dimension_object.history.all()[2].value)

        
        
    def test_overwrite_project(self):
        project = Project()
        project.id = 1
        project.save()

        d1 = DecimalDimension()
        d1.name = 'budjetti'
        d1.value = 5
        d1.save()

        pd1 = ProjectDimension()
        pd1.project = project
        pd1.dimension_object = d1
        pd1.save()

        from_data_array([[u'id', u'__history_date', u'Name'],
                        [u'1', '2013-03-16T17:41:28+00:00', 'foo']])

        self.assertEqual(1, Project.objects.get(id=1).dimensions.all().count())
        self.assertTrue(isinstance(Project.objects.get(id=1).dimensions.all()[0].dimension_object, TextDimension))

    def test_keep_unaffected_projects(self):
        project = Project()
        project.id = 1
        project.save()

        d1 = DecimalDimension()
        d1.name = 'budjetti'
        d1.value = 5
        d1.save()

        pd1 = ProjectDimension()
        pd1.project = project
        pd1.dimension_object = d1
        pd1.save()

        from_data_array([[u'id', u'__history_date', u'Name'],
                        [u'2', '2013-03-16T17:41:28+00:00', 'foo']])

        self.assertEqual(2, Project.objects.all().count())
        self.assertEqual(1, Project.objects.get(id=1).dimensions.all().count())
        self.assertTrue(isinstance(Project.objects.get(id=1).dimensions.all()[0].dimension_object, DecimalDimension))

        