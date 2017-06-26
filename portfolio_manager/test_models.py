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
from django.test import TestCase
from django.utils.timezone import make_aware

from portfolio_manager.models import TextDimension, DecimalDimension, DateDimension, AssociatedProjectsDimension, AssociatedPersonsDimension, \
    Project, Person, AssociatedPersonDimension, Organization, AssociatedOrganizationDimension, ProjectDimension, \
    Milestone, DimensionMilestone, DecimalMilestone, PathSnapshot, FourFieldSnapshot
from datetime import datetime
from django.utils import timezone
from portfolio_manager.importer import from_data_array


class DimensionsTestCase(TestCase):

    def setUp(self):
        pass

    fixtures = ['projects', 'persons', 'organizations', 'snapshot']

    def test_date_dimension(self):

        now = timezone.now()

        d = DateDimension()
        d.from_sheet('5/6/2015', now)
        d.save()

        self.assertEquals(1, d.history.all().count())
        self.assertEqual(make_aware(datetime(2015, 6, 5)), d.history.all()[0].value)
        self.assertEqual(now, d.history.all()[0].history_date)

    def test_associated_projects_dimension(self):

        project1 = Project.objects.get(pk=1)

        d = AssociatedProjectsDimension()
        d.from_sheet('1,2', None)
        d.save()

        project2 = Project.objects.get(pk=2)

        self.assertEquals(project1, d.value.all()[0])
        self.assertEquals(project2, d.value.all()[1])

    def test_associated_persons_dimension(self):

        person1 = Person.objects.get(pk=1)
        person2 = Person.objects.get(pk=2)

        d = AssociatedPersonsDimension()
        d.from_sheet('person1,person2,person3', None)
        d.save()

        person3 = Person.objects.get(first_name='person3')

        self.assertEquals(person1, d.value.all()[0])
        self.assertEquals(person2, d.value.all()[1])
        self.assertEquals(person3, d.value.all()[2])


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


    def test_path_snapshot(self):
        project = Project.objects.get(pk=1)
        x = TextDimension.objects.get(pk=1)
        y = DecimalDimension.objects.get(pk=1)

        snap = PathSnapshot()
        snap.name = 'TestSnap'
        snap.description = 'TestSnap Description'
        snap.snap_type = 'PA'
        snap.project = project
        snap.dimension_object_x = x
        snap.dimension_object_y = y
        snap.save()

        self.assertEquals(snap.project, project)
        self.assertEquals(snap.dimension_object_x, x)
        self.assertEquals(snap.dimension_object_y, y)


    def test_fourfield_snap(self):
        x = DecimalDimension.objects.get(pk=1)
        y = DecimalDimension.objects.get(pk=2)
        r = DecimalDimension.objects.get(pk=3)

        snap = FourFieldSnapshot()
        snap.name = "FF Snap"
        snap.description = "FF Snap Description"
        snap.snap_type = "FF"
        snap.x_dimension = x.name
        snap.y_dimension = y.name
        snap.radius_dimension = r.name
        snap.start_date = make_aware(datetime(2015, 6, 5))
        snap.end_date = make_aware(datetime(2015, 6, 6))
        snap.zoom = 100
        snap.save()

        self.assertEquals(snap.x_dimension, x.name)
        self.assertEquals(snap.y_dimension, y.name)
        self.assertEquals(snap.radius_dimension, r.name)

class CascadeDeleteTestCase(TestCase):

    def test_delete_organization(self):

        data = [[u'id', u'__history_date', u'Name', u'Budget', u'OwningOrganization'],
                ['', '', 'TEXT', 'NUM', 'AORG'],
                [u'1', '2012-03-16T17:41:28+00:00', 'foo', u'4', 'org1'],
                [u'm;28/6/2015', '2013-03-16T17:41:28+00:00', u'', u'5'],
                [u'm;29/6/2016', '2014-03-16T17:41:28+00:00', u'', u'9']]
        result = from_data_array(data)
        self.assertTrue(result['result'], 'Failed to validate field types in imported data')

        Organization.objects.get(pk='org1').delete()
        self.assertFalse(Organization.objects.all())
        self.assertFalse(Project.objects.all())
        self.assertFalse(ProjectDimension.objects.all())
        self.assertFalse(Milestone.objects.all())
        self.assertFalse(DimensionMilestone.objects.all())
        self.assertFalse(NumberMilestone.objects.all())
        # self.assertFalse(NameDimension.objects.all())
