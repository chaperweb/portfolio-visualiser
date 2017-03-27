from django.test import TestCase
from portfolio_manager.models import *
from portfolio_manager.forms import *

class FormsTestCase(TestCase):

	fixtures = [ 'organizations', 'persons' ]

	def test_text_dimension_form(self):
		project_form = AddProjectForm({'parent': 'org1', 'organization': 'org1', 'name': 'FooProject'});
		project_form.save()

		dimension_name = 'Phase'
		text_form = TextDimensionForm({'value': 'Closing'}, dimension_name=dimension_name, project_form=project_form )
		self.assertTrue(text_form.is_valid())
		text_form.save()

		self.assertEquals(1, project_form.instance.dimensions.all().count())
		self.assertEquals(dimension_name, project_form.instance.dimensions.all()[0].dimension_object.name)
		self.assertEquals('Closing', project_form.instance.dimensions.all()[0].dimension_object.value)
		self.assertEquals(1, project_form.instance.dimensions.all()[0].dimension_object.history.all().count())


	def test_add_project_form(self):
		form = AddProjectForm({'parent': 'org1', 'organization': 'org1', 'name': 'FooProject'});
		self.assertTrue(form.is_valid())
		form.save()
		project = Project.objects.get(name='FooProject')
		self.assertEquals(Organization.objects.get(pk='org1'), project.parent)

	def testAssociatedProjectsDimensionForm(self):
		project_form = AddProjectForm({'parent': 'org1', 'organization': 'org1', 'name': 'FooProject'});
		project_form.save()

		dimension_name = 'Dependencies'
		projects_form = AssociatedProjectsDimensionForm({'projects': [Project.objects.get(id=1).id]}, dimension_name=dimension_name, project_form=project_form )
		self.assertTrue(projects_form.is_valid())
		projects_form.save()

		self.assertEquals(1, project_form.instance.dimensions.all().count())
		self.assertEquals(dimension_name, project_form.instance.dimensions.all()[0].dimension_object.name)
		self.assertEquals(Project.objects.get(id=1), project_form.instance.dimensions.all()[0].dimension_object.projects.all()[0])
		self.assertEquals(1, project_form.instance.dimensions.all()[0].dimension_object.projects.all().count())


	def test_associated_persons_dimension_form(self):
		project_form = AddProjectForm({'parent': 'org1', 'organization': 'org1', 'name': 'FooProject'});
		project_form.save()

		dimension_name = 'Members'
		persons_form = AssociatedPersonsDimensionForm({'persons': [Person.objects.get(id=1).id,Person.objects.get(id=2).id]}, dimension_name=dimension_name, project_form=project_form )
		self.assertTrue(persons_form.is_valid())
		persons_form.save()

		self.assertEquals(1, project_form.instance.dimensions.all().count())
		self.assertEquals(dimension_name, project_form.instance.dimensions.all()[0].dimension_object.name)
		self.assertEquals(Person.objects.get(id=1), project_form.instance.dimensions.all()[0].dimension_object.persons.all()[0])
		self.assertEquals(Person.objects.get(id=2), project_form.instance.dimensions.all()[0].dimension_object.persons.all()[1])
		self.assertEquals(2, project_form.instance.dimensions.all()[0].dimension_object.persons.all().count())

	def test_associated_organization_dimension_form(self):
		project_form = AddProjectForm({'parent': 'org1', 'organization': 'org1', 'name': 'FooProject'});
		project_form.save()

		dimension_name = 'OwningOrganization'
		person_form = AssociatedOrganizationDimensionForm({'value': Organization.objects.get(pk='org1').pk}, dimension_name=dimension_name, project_form=project_form )
		self.assertTrue(person_form.is_valid())
		person_form.save()

		self.assertEquals(1, project_form.instance.dimensions.all().count())
		self.assertEquals(dimension_name, project_form.instance.dimensions.all()[0].dimension_object.name)
		self.assertEquals(Organization.objects.get(pk='org1'), project_form.instance.dimensions.all()[0].dimension_object.value)
		self.assertEquals(1, project_form.instance.dimensions.all()[0].dimension_object.history.all().count())


	def test_associated_person_dimension_form(self):
		project_form = AddProjectForm({'parent': 'org1', 'organization': 'org1', 'name': 'FooProject'});
		project_form.save()

		dimension_name = 'Manager'
		person_form = AssociatedPersonDimensionForm({'value': Person.objects.get(id=1).id}, dimension_name=dimension_name, project_form=project_form )
		self.assertTrue(person_form.is_valid())
		person_form.save()

		self.assertEquals(1, project_form.instance.dimensions.all().count())
		self.assertEquals(dimension_name, project_form.instance.dimensions.all()[0].dimension_object.name)
		self.assertEquals(Person.objects.get(id=1), project_form.instance.dimensions.all()[0].dimension_object.value)
		self.assertEquals(1, project_form.instance.dimensions.all()[0].dimension_object.history.all().count())


	def test_date_dimension_form(self):
		project_form = AddProjectForm({'parent': 'org1', 'organization': 'org1', 'name': 'FooProject'});
		project_form.save()

		dimension_name = 'StartDate'
		date_form = DateDimensionForm({'value': '1/8/2015'}, dimension_name=dimension_name, project_form=project_form )
		self.assertTrue(date_form.is_valid())
		date_form.save()

		self.assertEquals(1, project_form.instance.dimensions.all().count())
		self.assertEquals(dimension_name, project_form.instance.dimensions.all()[0].dimension_object.name)
		self.assertEquals(parse('1/8/2015', dayfirst=True).replace(tzinfo=pytz.utc), project_form.instance.dimensions.all()[0].dimension_object.value)
		self.assertEquals(1, project_form.instance.dimensions.all()[0].dimension_object.history.all().count())


	def test_decimal_dimension_form(self):
		project_form = AddProjectForm({'parent': 'org1', 'organization': 'org1', 'name': 'FooProject'});
		project_form.save()

		dimension_name = 'Size'
		decimal_form = DecimalDimensionForm({'value': 1}, dimension_name=dimension_name, project_form=project_form )
		self.assertTrue(decimal_form.is_valid())
		decimal_form.save()

		self.assertEquals(1, project_form.instance.dimensions.all().count())
		self.assertEquals(dimension_name, project_form.instance.dimensions.all()[0].dimension_object.name)
		self.assertEquals(1, project_form.instance.dimensions.all()[0].dimension_object.value)
		self.assertEquals(1, project_form.instance.dimensions.all()[0].dimension_object.history.all().count())
