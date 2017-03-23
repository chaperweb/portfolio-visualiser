from django.test import TestCase
from portfolio_manager.models import *
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import *
from portfolio_manager.serializers import *
from rest_framework.renderers import JSONRenderer
from django.test import Client
from django.core.urlresolvers import reverse
import json
from portfolio_manager.importer import from_data_array
from portfolio_manager import views

class SerializersTestCase(TestCase):
  
        def test_milestones_serializer(self):
                from_data_array([[u'id', u'__history_date', u'Name', u'SizeMoney'],
                        [u'1', '2012-03-16T17:41:28+00:00', 'foo', u'4'],
                        [u'm;28/6/2015', '2013-03-16T17:41:28+00:00', u'', u'5'],
                        [u'm;29/6/2016', '2014-03-16T17:41:28+00:00', u'', u'9']])
                
                milestones1_serializer = MilestoneHistorySerializer(Project.objects.get(id=1).milestones.all()[0].history.all()[0])
                milestones2_serializer = MilestoneHistorySerializer(Project.objects.get(id=1).milestones.all()[1].history.all()[0])


                expected_serialization = [
                                           {
                                              'dimensions':[
                                                 {
                                                    'dimension_milestone_object':{
                                                       'value':'5.00'
                                                    },
                                                    'project_dimension':2
                                                 }
                                              ],
                                              'due_date':'2015-06-28T00:00:00Z'
                                           },
                                           {
                                              'dimensions':[
                                                   {
                                                      'dimension_milestone_object':{
                                                         'value':'9.00'
                                                      },
                                                      'project_dimension':2
                                                   }
                                                ],
                                                'due_date':'2016-06-29T00:00:00Z'
                                            }
                                        ]

                self.assertEquals(expected_serialization, [milestones1_serializer.data, milestones2_serializer.data])

        def test_project_serializer(self):

                from_data_array([[u'id', u'__history_date', u'Name', u'SizeMoney'],
                        [u'1', '2012-03-16T17:41:28+00:00', 'foo', u'4'],
                        [u'm;28/6/2015', '2013-03-16T17:41:28+00:00', u'', u'5'],
                        [u'm;29/6/2016', '2014-03-16T17:41:28+00:00', u'', u'9'],
                        [u'2', '2017-16-03T17:41:28+00:00', 'biz', u'4']])
                
                projects_serializer = ProjectSerializer(Project.objects.all(), many=True)

                expected_serialization = [
                           {
                              'id':1,
                              'name':'foo',
                              'dimensions':[
                                 {
                                    'id':1,
                                    'dimension_object':{
                                       'history':[
                                          {
                                             'value':'foo',
                                             'id':1,
                                             'history_date':'2012-03-16T17:41:28Z',
                                             'string': 'foo'
                                          }
                                       ],
                                       'name':'Name'
                                    },
                                    'dimension_type': 'TextDimension'
                                 },
                                 {
                                    'id':2,
                                    'dimension_object':{
                                       'history':[
                                          {
                                             'value':4.0,
                                             'id':1,
                                             'history_date':'2012-03-16T17:41:28Z',
                                             'string': '4.00'
                                          }
                                       ],
                                       'name':'SizeMoney'
                                    },
                                    'dimension_type': 'DecimalDimension'
                                 }
                              ],
                              'milestones':[
                                 {
                                    'due_date':'2015-06-28T00:00:00Z',
                                    'dimensions':[
                                       {
                                          'dimension_milestone_object':{
                                             'value':'5.00'
                                          },
                                          'project_dimension':2
                                       }
                                    ]
                                 },
                                 {
                                    'due_date':'2016-06-29T00:00:00Z',
                                    'dimensions':[
                                       {
                                          'dimension_milestone_object':{
                                             'value':'9.00'
                                          },
                                          'project_dimension':2
                                       }
                                    ]
                                 }
                              ]
                           },
                           {
                              'id':2,
                              'name':'biz',
                              'dimensions':[
                                 {
                                    'id':3,
                                    'dimension_object':{
                                       'history':[
                                          {
                                             'value':'biz',
                                             'id':2,
                                             'history_date':'2017-03-16T17:41:28Z',
                                             'string': 'biz'
                                          }
                                       ],
                                       'name':'Name'
                                    },
                                    'dimension_type': 'TextDimension'
                                 },
                                 {
                                    'id':4,
                                    'dimension_object':{
                                       'history':[
                                          {
                                             'value':4.0,
                                             'id':2,
                                             'history_date':'2017-03-16T17:41:28Z',
                                             'string': '4.00'
                                          }
                                       ],
                                       'name':'SizeMoney'
                                    },
                                    'dimension_type': 'DecimalDimension'
                                 }
                              ],
                              'milestones':[

                              ]
                           }
                        ]
                self.assertEquals(expected_serialization, projects_serializer.data)

        