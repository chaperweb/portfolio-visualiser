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
# coding=utf-8
from django.test import TestCase
from portfolio_manager import views
from django.http import JsonResponse
from portfolio_manager.importer import from_data_array


class ViewsTestCase(TestCase):
    def test_json_unicode_encoding(self):
        # Tests that non-ascii characters are importer successfully

        data = [[u'id', u'__history_date', u'Name',
                 u'ProjectManagerDimension',
                 u'ProjectDependenciesDimension',
                 u'Members'],
                ['', '', 'TEXT', 'APER', 'APROJ', 'APERS'],
                [u'1', '2012-03-16T17:41:28+00:00', u'Biz', u'Urho', u'', u'Matti, Pekka'],
                [u'2', '2012-04-16T17:41:28+00:00', u'Böz', u'Yrjö', u'1', u'Päivö, Väinämö']]
        result = from_data_array(data)
        self.assertTrue(result['result'], 'Failed to validate field types in imported data')

        json_response = views.json(None)
        self.assertIsInstance(json_response, JsonResponse)
