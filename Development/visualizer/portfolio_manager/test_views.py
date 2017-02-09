from django.test import TestCase
from portfolio_manager.models import *
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import *
from portfolio_manager.serializers import ProjectSerializer
from rest_framework.renderers import JSONRenderer
from django.test import Client
from django.core.urlresolvers import reverse
import json

class ViewsTestCase(TestCase):

        def setUp(self):
                pass

        def test_json_decimal_dimension(self):

                project = Project()
                project.name = 'projekti'
                project.save()

                d1 = DecimalDimension()
                d1.name = 'budjetti'
                d1.value = 2
                d1._history_date = '2016-01-30T05:55:14.372793Z'
                d1.save()

                m = DecimalDimensionMilestone()
                m.value = 6
                m.decimal_dimension = d1
                m.at = '2016-01-30T05:55:14.372793Z'
                m.save()

                pd1 = ProjectDimension()
                pd1.project = project
                pd1.dimension_object = d1
                pd1.save()

                d2 = DecimalDimension()
                d2.name = 'tyotunnit'
                d2.value = 3
                d2._history_date = '2016-01-30T05:55:14.372793Z'
                d2.save()

                pd2 = ProjectDimension()
                pd2.project = project
                pd2.dimension_object = d2
                pd2.save()

                client = Client()
                response = client.get(reverse('json', args=[1]))
                self.assertEquals(200, response.status_code)
                self.maxDiff = None
                expected_response = {u"id": 1, u"name": u"projekti", u"dimensions": [{u"id": 1, u"dimension_object": {u"id": 1, u"name": u"budjetti", u"milestones": [{u"id": 1, u"value": u'6.00', u"at": u'2016-01-30T05:55:14.372793Z'}], u"history": [{u"id": 1, u"value": u'2.00', u"history_date": u"2016-01-30T05:55:14.372793Z"}]}}, {u"id": 2, u"dimension_object": {u"id": 2, u"name": u"tyotunnit", u"milestones": [], u"history": [{u"id": 2, u"value": u'3.00', u"history_date": u"2016-01-30T05:55:14.372793Z"}]}}]}
                self.assertEquals(expected_response, json.loads(response.content))
