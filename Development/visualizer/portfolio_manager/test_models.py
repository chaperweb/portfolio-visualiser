from django.test import TestCase
from portfolio_manager.models import *
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import *
from portfolio_manager.serializers import ProjectSerializer
from rest_framework.renderers import JSONRenderer
from portfolio_manager.importer import from_data_array

class DimensionsTestCase(TestCase):

    def setUp(self):
        pass

    fixtures = ['projects', 'persons', 'organizations']

    def test_date_dimension(self):

        now = timezone.now()

        d = DateDimension()
        d.from_sheet('5/6/2015', now)
        d.save()

        self.assertEquals(1, d.history.all().count())
        self.assertEqual(datetime(2015,6,5,tzinfo=pytz.utc), d.history.all()[0].value)
        self.assertEqual(now, d.history.all()[0].history_date)

    def test_associated_projects_dimension(self):

        project1 = Project.objects.get(pk=1)

        d = AssociatedProjectsDimension()
        d.from_sheet('1,2', None)
        d.save()

        project2 = Project.objects.get(pk=2)

        self.assertEquals(project1, d.projects.all()[0])
        self.assertEquals(project2, d.projects.all()[1])

    def test_associated_persons_dimension(self):

        person1 = Person.objects.get(pk=1)
        person2 = Person.objects.get(pk=2)

        d = AssociatedPersonsDimension()
        d.from_sheet('person1,person2,person3', None)
        d.save()

        person3 = Person.objects.get(first_name='person3')
        
        self.assertEquals(person1, d.persons.all()[0])
        self.assertEquals(person2, d.persons.all()[1])
        self.assertEquals(person3, d.persons.all()[2])


    def test_associated_person_dimension_person_exists(self):

        now = timezone.now()
        person1 = Person.objects.get(pk=1)

        d = AssociatedPersonDimension()
        d.from_sheet('person1', now)
        d.save()
        
        self.assertEquals(person1, d.value)
        self.assertEquals(person1, d.history.all()[0].value)
        self.assertEqual(now, d.history.all()[0].history_date)

    def test_associated_person_dimension_person_doesnt_exists(self):

        now = timezone.now()

        d = AssociatedPersonDimension()
        d.from_sheet('person3', now)
        d.save()

        person3 = Person.objects.get(first_name='person3')
        
        self.assertEquals(person3, d.value)
        self.assertEquals(person3, d.history.all()[0].value)
        self.assertEqual(now, d.history.all()[0].history_date)

    def test_associated_organization_dimension_org_exists(self):

        now = timezone.now()
        org1 = Organization.objects.get(pk='org1')

        d = AssociatedOrganizationDimension()
        d.from_sheet('org1', now)
        d.save()

        self.assertEquals(org1, d.value)
        self.assertEquals(org1, d.history.all()[0].value)
        self.assertEqual(now, d.history.all()[0].history_date)

    def test_associated_organization_dimension_org_not_exists(self):

        now = timezone.now()
        
        d = AssociatedOrganizationDimension()
        d.from_sheet('org2', now)
        d.save()

        org1 = Organization.objects.get(pk='org2')

        self.assertEquals(org1, d.value)
        self.assertEquals(org1, d.history.all()[0].value)
        self.assertEqual(now, d.history.all()[0].history_date)

class CascadeDeleteTestCase(TestCase):

    def test_delete_organization(self):

        from_data_array([[u'id', u'__history_date', u'Name', u'SizeMoney', u'OwningOrganization'],
                        [u'1', '2012-03-16T17:41:28+00:00', 'foo', u'4', 'org1'],
                        [u'm;28/6/2015', '2013-03-16T17:41:28+00:00', u'', u'5'],
                        [u'm;29/6/2016', '2014-03-16T17:41:28+00:00', u'', u'9']])

        Organization.objects.get(pk='org1').delete()
        self.assertFalse(Organization.objects.all())
        self.assertFalse(Project.objects.all())
        self.assertFalse(ProjectDimension.objects.all())
        self.assertFalse(Milestone.objects.all())
        self.assertFalse(DimensionMilestone.objects.all())
        self.assertFalse(DecimalMilestone.objects.all())
        self.assertFalse(NameDimension.objects.all())


    
    


   

   
    
