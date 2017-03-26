# coding=utf-8
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from django.urls import reverse
from selenium.webdriver.firefox.webdriver import WebDriver as Firefox 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from portfolio_manager.models import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from decimal import *
from pyvirtualdisplay import Display

class SeleniumTestCase(LiveServerTestCase):

    def open(self, url):
        self.selenium.get("%s%s" % (self.live_server_url, url))

class CustomFirefoxWebDriver(Firefox):

    def find_css(self, css_selector):

        elems = self.find_elements_by_css_selector(css_selector)
        found = len(elems)
        if found == 1:
            return elems[0]
        elif not elems:
            raise NoSuchElementException(css_selector)
        return elems

    def wait_for_css(self, css_selector, timeout=7):

        return WebDriverWait(self, timeout).until(lambda driver : driver.find_css(css_selector))

class BrowserTestCase(SeleniumTestCase):

    fixtures = [ 'organizations', 'project_templates', 'persons' ]

    def setUp(self):
        
        self.vdisplay = Display(visible=0, size=(1024, 768))
        self.vdisplay.start()
        self.selenium = CustomFirefoxWebDriver()
        self.selenium.maximize_window()

        super(BrowserTestCase, self).setUp()

    def tearDown(self):
        
        super(BrowserTestCase, self).tearDown()

        self.selenium.quit()
        self.vdisplay.stop()

    def test_add_organization(self):
        self.open(reverse('admin_tools'))

        add_organization_name = 'Örganizaatio'
        self.selenium.find_element_by_id('orgName').send_keys(add_organization_name)
        self.selenium.find_element_by_id('org-form').submit()
        self.selenium.wait_for_css('#conf-modal-body > h3');

        self.assertTrue('Organization created: '+add_organization_name in self.selenium.page_source)
        organization = Organization.objects.get(pk=add_organization_name)
        self.assertIsInstance(organization, Organization)
        templates = organization.templates.all()
        self.assertEquals(1, templates.count())
        template = templates[0]
        self.assertEquals('default', template.name)
        self.assertEquals(3, template.dimensions.all().count())
        template_dimensions = template.dimensions.all()
        self.assertEquals(DecimalDimension, template_dimensions[0].content_type.model_class())
        self.assertEquals('SizeMoney', template_dimensions[0].name)
        self.assertEquals(DateDimension, template_dimensions[1].content_type.model_class())
        self.assertEquals('EndDate', template_dimensions[1].name)
        self.assertEquals(AssociatedPersonDimension, template_dimensions[2].content_type.model_class())
        self.assertEquals('ProjectManager', template_dimensions[2].name)


    def test_add_organization_add_project(self):
        self.open(reverse('admin_tools'))

        organization_name = 'Great organization'
        self.selenium.find_element_by_id('orgName').send_keys(organization_name)
        self.selenium.find_element_by_id('org-form').submit()
        self.selenium.wait_for_css('#conf-modal-body > h3');
 
        self.open(reverse('admin_tools')) # Reload organizations in "Add project" modal

        project_name = "Great project"
        self.selenium.find_element_by_id('id_name').send_keys(project_name)
        Select(self.selenium.find_element_by_id('id_organization')).select_by_value(organization_name)
        self.selenium.find_element_by_id('pre-add-project-form').submit()

        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located((By.ID, 'id_add_project_form-name'))
        )

        organization = Organization.objects.get(pk=organization_name)

        project_size_money = '135151.00'
        template_dimension = organization.templates.all()[0].dimensions.all()[0]
        self.selenium.find_element_by_id('id_'+str(template_dimension.id)+'_form-value').send_keys(project_size_money)
       
        project_end_date = '1/8/2015'
        template_dimension = organization.templates.all()[0].dimensions.all()[1]
        self.selenium.find_element_by_id('id_'+str(template_dimension.id)+'_form-value').send_keys(project_end_date)
        
        project_project_manager = Person.objects.get(id=1)
        template_dimension = organization.templates.all()[0].dimensions.all()[2]
        Select(self.selenium.find_element_by_id('id_'+str(template_dimension.id)+'_form-value')).select_by_value(str(project_project_manager.id))
        
        self.selenium.find_element_by_id('add-project-form').submit()

        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located((By.ID, 'project-dimension-panels'))
        )

    def test_add_project_from_admin_tools(self):
        self.open(reverse('admin_tools'))
        self._test_add_project()

    def test_add_project_from_homepage(self):

        self.open(reverse('homepage'))
        self.selenium.find_element_by_id('add-project-btn').click()

        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located((By.ID, "id_name"))
        )

        self._test_add_project()

    def _test_add_project(self):

        project_name = "FooBar"
        project_organization = Organization.objects.get(pk='org1')

        self.selenium.find_element_by_id('id_name').send_keys(project_name)
        Select(self.selenium.find_element_by_id('id_organization')).select_by_value(project_organization.pk)
        self.selenium.find_element_by_id('pre-add-project-form').submit()

        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located((By.ID, 'id_add_project_form-name'))
        )

        self.assertEquals(project_name, self.selenium.find_element_by_id('id_add_project_form-name').get_attribute('value'))
        self.assertEquals(project_organization.pk, self.selenium.find_element_by_id('id_add_project_form-organization').get_attribute('value'))

        project_phase = "Pre-study"
        template_dimension = project_organization.templates.all()[0].dimensions.all()[0]
        self.selenium.find_element_by_id('id_'+str(template_dimension.id)+'_form-value').send_keys(project_phase)
       
        project_size = '135151.00'
        template_dimension = project_organization.templates.all()[0].dimensions.all()[1]
        self.selenium.find_element_by_id('id_'+str(template_dimension.id)+'_form-value').send_keys(project_size)
        self.selenium.find_element_by_id('add-project-form').submit()

        WebDriverWait(self.selenium, 10).until(
            EC.visibility_of_element_located((By.ID, 'project-dimension-panels'))
        )

        self.assertEquals(project_name, self.selenium.find_element_by_id('project-name').text)
        self.assertEquals(project_organization.pk, self.selenium.find_element_by_id('projectparent').text)
        self.assertEquals(project_phase, self.selenium.find_element_by_id('Phase').text)
        self.assertEquals(project_size, self.selenium.find_element_by_id('Size').text)

        project = Project.objects.get(name=project_name)
        self.assertIsInstance(project, Project)
        self.assertEquals(project_organization, project.parent)
        dimensions = project.dimensions.all()
        self.assertEquals(2, dimensions.count())
        self.assertIsInstance(dimensions[0].dimension_object, TextDimension)
        self.assertEquals(project_phase, dimensions[0].dimension_object.value)
        self.assertIsInstance(dimensions[1].dimension_object, DecimalDimension)
        self.assertEquals(Decimal(project_size), dimensions[1].dimension_object.value)



        

