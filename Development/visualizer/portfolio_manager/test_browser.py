# coding=utf-8
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class BrowserTestCase(LiveServerTestCase):

    def setUp(self):
        self.selenium = webdriver.Firefox()
        super(BrowserTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(BrowserTestCase, self).tearDown()

    def test_add_organization(self):
        selenium = self.selenium

        selenium.get('http://127.0.0.1:8000/admin_tools')

        add_organization_name = 'Örganizaatio'
        selenium.find_element_by_id('orgName').send_keys(add_organization_name)
        selenium.find_element_by_id('org-form').submit()

        assert 'Organization created: '+add_organization_name in selenium.page_source