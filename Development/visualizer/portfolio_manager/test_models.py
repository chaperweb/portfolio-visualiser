from django.test import TestCase
from models import *
from datetime import datetime, timedelta
from django.utils import timezone

class ModelsTestCase(TestCase):
    def setUp(self):
      pass
        
    def test_project_dimensions_and_milestones(self):
        """Test project dimensions and milestones"""

        project = Project()
        project.name = 'projekti'
        project.save()

        d1 = NumericDimension()
        d1.name = 'budjetti'
        d1.value = 5;
        d1.save()

        pd1 = ProjectDimension()
        pd1.project = project
        pd1.dimension_object = d1
        pd1.save()

        now = timezone.now()
        project_milestone = ProjectMilestone()
        project_milestone.deadline = now + timedelta(days=4)
        project_milestone.project = project
        project_milestone.save()

        d1_milestone = NumericDimensionMilestone()
        d1_milestone.numeric_dimension = d1
        d1_milestone.value = 7
        d1_milestone.save()

        project_milestone_d1_milestone = ProjectMilestoneDimensionMilestone()
        project_milestone_d1_milestone.project_milestone = project_milestone
        project_milestone_d1_milestone.dimension_milestone_object = d1_milestone
        project_milestone_d1_milestone.save()

        self.assertEqual(len(project.dimensions.all()), 1)
        self.assertEqual(project.dimensions.all()[0].dimension_object.name, 'budjetti')
        self.assertEqual(len(project.milestones.all()), 1)
        self.assertEqual(project.milestones.all()[0].dimension_milestones.all()[0].dimension_milestone_object.value, 7)

        project.dimensions.all()[0].dimension_object.update_value(4, now + timedelta(days=1));
        project.dimensions.all()[0].dimension_object.update_value(6, now + timedelta(days=2));

        self.assertEqual(project.dimensions.all()[0].dimension_object.value, 6)
        self.assertEqual(project.milestones.all()[0].on_schedule(), False)

        project.dimensions.all()[0].dimension_object.update_value(7, now + timedelta(days=3));
        self.assertEqual(project.milestones.all()[0].on_schedule(), True)

    def test_members_dimension(self):

        project = Project()
        project.name = 'projekti'
        project.save()

        d1 = MembersDimension()
        d1.save()

        pd1 = ProjectDimension()
        pd1.project = project
        pd1.dimension_object = d1
        pd1.save()

        person1 = Person();
        person1.first_name = 'first first'
        person1.last_name = 'first last'
        person1.save()

        person2 = Person()
        person2.first_name = 'second first'
        person2.last_name = 'second last'
        person2.save()

        d1.set_members([person1])
        d1.set_members([person1, person2])
        d1.set_members([person2])

        self.assertEqual(len(d1.members.all()), 1)
        self.assertEqual(d1.members.all()[0].first_name, 'second first')

        versions = Version.objects.get_for_object(d1)
        self.assertEqual(len(versions), 3)

        self.assertEqual(len(versions[1].field_dict['members']), 2)
        self.assertEqual(Person.objects.get(pk=versions[1].field_dict['members'][0]).first_name, 'first first')
        self.assertEqual(Person.objects.get(pk=versions[1].field_dict['members'][1]).first_name, 'second first')

