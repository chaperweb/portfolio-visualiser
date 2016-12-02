from django.test import TestCase
from models import *
from datetime import datetime, timedelta
from django.utils import timezone

class ModelsTestCase(TestCase):
    def setUp(self):

        self.project = Project()
        self.project.name = 'projekti'
        self.project.save()

        d1 = NumericDimension()
        d1.initial_value = 5
        d1.name = 'budjetti'
        d1.save()

        self.now = timezone.now()
        d1.set_milestone(self.now + timedelta(days=4), 7)

        pd1 = ProjectDimension()
        pd1.project = self.project
        pd1.dimension_object = d1
        pd1.save()
      
    def test_progress(self):
        """Test progress of numeric dimension"""

        self.project.dimensions.all()[0].dimension_object.update_progress(self.now + timedelta(days=1), -1);
        self.project.dimensions.all()[0].dimension_object.update_progress(self.now + timedelta(days=2), 2);

        self.assertEqual(self.project.dimensions.all()[0].dimension_object.get_status(), 6)
        self.assertEqual(self.project.on_schedule(self.now + timedelta(days=5)), False)

        self.project.dimensions.all()[0].dimension_object.update_progress(self.now + timedelta(days=3), 1);
        self.assertEqual(self.project.on_schedule(self.now + timedelta(days=5)), True)