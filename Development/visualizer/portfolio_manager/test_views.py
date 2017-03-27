# coding=utf-8
from django.test import TestCase
from portfolio_manager import views
from django.http import JsonResponse
from portfolio_manager.importer import from_data_array

class ViewsTestCase(TestCase):

	def test_json_unicode_encoding(self):

		# Tests that non-ascii characters are importer successfully
		
		from_data_array([[u'id', u'__history_date', u'Name', 
						  u'ProjectManagerDimension', 
						  u'ProjectDependenciesDimension', 
						  u'Members'],
						[u'1', '2012-03-16T17:41:28+00:00', u'Biz', u'Urho', u'', u'Matti, Pekka'],
                        [u'2', '2012-04-16T17:41:28+00:00', u'Böz', u'Yrjö', u'1', u'Päivö, Väinämö']])

		json_response = views.json(None)
		self.assertIsInstance(json_response, JsonResponse)
