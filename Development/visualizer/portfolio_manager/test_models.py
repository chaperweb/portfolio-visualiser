from django.test import TestCase
from models import *
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import *
from serializers import ProjectSerializer
from rest_framework.renderers import JSONRenderer

class ModelsTestCase(TestCase):

    def setUp(self):
        pass

    def test_serialize_project(self):
        project = Project()
        project.name = 'projekti'
        project.save()

        d1 = DecimalDimension()
        d1.name = 'budjetti'
        d1.value = 2
        d1.save()

        m = DecimalDimensionMilestone()
        m.value = 6
        m.decimal_dimension = d1
        m.at = timezone.now()
        m.save()

        pd1 = ProjectDimension()
        pd1.project = project
        pd1.dimension_object = d1
        pd1.save()

        d2 = DecimalDimension()
        d2.name = 'tyotunnit'
        d2.value = 3
        d2.save()

        pd2 = ProjectDimension()
        pd2.project = project
        pd2.dimension_object = d2
        pd2.save()

        serializer = ProjectSerializer(project)
        self.assertEqual('', JSONRenderer().render(serializer.data))


    def test_import_models_data(self):
        data = [[u'id', u'__history_date', u'Name', u'StartDate', u'EndDate', u'ProjectOwner', u'OwningOrganization', u'ProjectManager', u'Customer', u'Department', u'SizeMoney', u'SizeManDays', u'SizeEffect', u'Description', u'Technology', u'ProjectDependencies', u'DevelopmentModel', u'Vendor', u'Members', u'Phase'],
                [u'1', u'25/12/2014', u'Project1', u'1/1/2015', u'15/6/2015', u'Mister1', u'Org1', u'Pm1', u'Customer1', u'Postal',
                    u'100000', u'100', u'3', u'Improvement1', u'Python, NoSql', u'', u'Waterfall', u'Taito', u'Pena, Antti', u'Phase1'],
                [u'1', u'', u'', u'1/1/2015', u'15/6/2015', u'', u'', u'', u'',
                    u'', u'', u'', u'', u'', u'', u'', u'', u'', u'', u'Phase2'],
                [u'1', u'', u'', u'3/4/2015', u'15/6/2015', u'', u'', u'', u'',
                 u'', u'', u'', u'', u'', u'', u'', u'', u'', u'', u'Phase3'],
                [u'1', u'5/6/2015', u'', u'15/6/2015', u'8/7/2015', u'', u'', u'Pm9', u'',
                 u'', u'89765', u'88', u'4', u'', u'', u'', u'', u'', u'Pena, Antti, Kalle'],
                [u'1', u'2/7/2015', u'', u'15/6/2015', u'4/8/2015', u'', u'', u'',
                 u'', u'', u'', u'', u'', u'', u'', u'', u'', u'', u'', u'Phase4'],
                [u'1', u'28/7/2015', u'', u'1/1/2015', u'30/8/2015'], [u'2', u'7/12/2015', u'Project2', u'1/1/2016', u'27/12/2015', u'Mister2', u'Org2', u'Pm2',
                                                                       u'Customer2', u'Sales', u'200000', u'123', u'8', u'More monet', u'Java, Perl, Aws', u'1', u'Agile', u'HKI', u'Ilana, Simon, Barry', u'Prestudy'],
                [u'2', u'', u'', u'1/1/2016', u'27/12/2015'],
                [u'2', u'', u'', u'1/1/2016', u'27/12/2015'],
                [u'2', u'4/12/2015', u'', u'1/1/2016', u'17/1/2016', u'', u'', u'', u'',
                 u'', u'222222', u'133', u'', u'', u'', u'', u'', u'', u'', u'Alfa'],
                [u'2', u'7/1/2016', u'', u'1/1/2016', u'20/2/2016', u'', u'', u'Pm3', u'',
                 u'', u'222456', u'145', u'', u'', u'', u'', u'', u'', u'', u'Beta'],
                [u'2', u'15/2/2016', u'', u'1/1/2016', u'30/3/2016',
                 u'', u'', u'', u'', u'', u'345000', u'200'],
                [u'2', u'14/3/2015', u'', u'1/1/2016', u'27/4/2015', u'', u'', u'',
                 u'', u'', u'', u'', u'', u'', u'', u'', u'', u'', u'', u'Done'],
                [u'2', u'', u'', u'1/1/2016']]

        import_models_data(data)
        self.assertEqual(2,Project.objects.all().count())
        self.assertEqual(16, Project.objects.get(pk=1).dimensions.all().count())
        self.assertEqual('Project1', Project.objects.get(pk=1).dimensions.all()[0].dimension_object.value)
        self.assertEqual('Project2', Project.objects.get(pk=2).dimensions.all()[0].dimension_object.value)
        self.assertEqual(2, ProjectDimension.objects.get(project_id=1, content_type=ContentType.objects.get_for_model(globals()["ProjectManagerDimension"])).dimension_object.history.all().count())
        self.assertEqual(4, ProjectDimension.objects.get(project_id=1, content_type=ContentType.objects.get_for_model(globals()["PhaseDimension"])).dimension_object.history.all().count())

    def test_clear_projects_before_import(self):
        project_to_be_removed = Project()
        project_to_be_removed.id = 10
        project_to_be_removed.save()
        self.assertEqual(1,Project.objects.all().count())
        import_models_data([[u'id', u'__history_date', u'Name']])
        self.assertEqual(0,Project.objects.all().count())

    def test_size_money_dimension(self):

        d1 = SizeMoneyDimension()
        d1.name = 'size_money'
        d1.value = 0
        d1.save()

        d1.update_value(1)
        d1.update_value(5.4)

        versions = Version.objects.get_for_object(d1)
        self.assertEqual(len(versions), 2)

        self.assertEqual(versions[0].field_dict['value'], Decimal(
            '5.4').quantize(Decimal(10) ** -2))
        self.assertEqual(versions[1].field_dict['value'], 1)

    def test_development_method_dimension(self):

        d1 = DevelopmentMethodDimension()
        d1.name = 'development method'
        d1.value = ''
        d1.save()

        d1.update_value('java')
        d1.update_value('scala')

        versions = Version.objects.get_for_object(d1)
        self.assertEqual(len(versions), 2)

        self.assertEqual(versions[0].field_dict['value'], 'scala')
        self.assertEqual(versions[1].field_dict['value'], 'java')

    def test_project_id(self):
        project = Project()
        project.name = 'projekti'
        project.save()
        self.assertEqual(project.id, 1)

    def test_start_time_dimension(self):

        d1 = StartTimeDimension()
        d1.name = 'start time'
        d1.value = timezone.now()
        d1.save()

        now = timezone.now()
        d1.update_value(now)
        d1.update_value(now + timedelta(days=5))

        versions = Version.objects.get_for_object(d1)
        self.assertEqual(len(versions), 2)

        self.assertEqual(versions[0].field_dict['value'].replace(
            microsecond=0), now.replace(microsecond=0) + timedelta(days=5))
        self.assertEqual(versions[1].field_dict['value'].replace(
            microsecond=0), now.replace(microsecond=0))

    def test_milestones_dimension(self):
        project = Project()
        project.name = 'projekti'
        project.save()

        d1 = MilestonesDimension()
        d1.name = 'milestones'
        d1.save()

        pd1 = ProjectDimension()
        pd1.project = project
        pd1.dimension_object = d1
        pd1.save()

        now = timezone.now()
        p_milestone1 = ProjectMilestone()
        p_milestone1.deadline = now + timedelta(days=4)
        p_milestone1.save()

        p_milestone2 = ProjectMilestone()
        p_milestone2.deadline = now + timedelta(days=5)
        p_milestone2.save()

        d1.set_milestones([p_milestone1, p_milestone2])
        d1.set_milestones([p_milestone2])

        p_milestone2.deadline = now + timedelta(days=6)
        p_milestone2.save()
        d1.save()

        first_version = Version.objects.get_for_object(d1)[1]
        first_version_project_milestones = first_version.revision.version_set.filter(
            content_type=ContentType.objects.get_for_model(ProjectMilestone))
        self.assertEqual(len(first_version_project_milestones), 2)
        self.assertEqual(first_version_project_milestones[0].field_dict['deadline'].replace(
            microsecond=0), now.replace(microsecond=0) + timedelta(days=4))
        self.assertEqual(first_version_project_milestones[1].field_dict['deadline'].replace(
            microsecond=0), now.replace(microsecond=0) + timedelta(days=5))

    def test_project_dimensions_and_milestones(self):
        """Test project dimensions and milestones"""

        project = Project()
        project.name = 'projekti'
        project.save()

        d1 = NumericDimension()
        d1.name = 'budjetti'
        d1.value = 5
        d1.save()

        d2 = MilestonesDimension()
        d2.name = 'milestones'
        d2.save()

        pd1 = ProjectDimension()
        pd1.project = project
        pd1.dimension_object = d1
        pd1.save()

        pd2 = ProjectDimension()
        pd2.project = project
        pd2.dimension_object = d2
        pd2.save()

        now = timezone.now()
        project_milestone = ProjectMilestone()
        project_milestone.deadline = now + timedelta(days=4)
        project_milestone.save()
        d2.set_milestones([project_milestone])

        d1_milestone = NumericDimensionMilestone()
        d1_milestone.numeric_dimension = d1
        d1_milestone.value = 7
        d1_milestone.save()

        project_milestone_d1_milestone = ProjectMilestoneDimensionMilestone()
        project_milestone_d1_milestone.project_milestone = project_milestone
        project_milestone_d1_milestone.dimension_milestone_object = d1_milestone
        project_milestone_d1_milestone.save()

        self.assertEqual(len(project.dimensions.all()), 2)
        self.assertEqual(project.dimensions.all()[
                         0].dimension_object.name, 'budjetti')
        self.assertEqual(project.dimensions.all()[
                         1].dimension_object.name, 'milestones')
        self.assertEqual(len(project.dimensions.all()[
                         1].dimension_object.milestones.all()), 1)
        self.assertEqual(project.dimensions.all()[1].dimension_object.milestones.all()[
                         0].dimension_milestones.all()[0].dimension_milestone_object.value, 7)

        project.dimensions.all()[0].dimension_object.update_value(
            4, now + timedelta(days=1))
        project.dimensions.all()[0].dimension_object.update_value(
            6, now + timedelta(days=2))

        self.assertEqual(project.dimensions.all()[0].dimension_object.value, 6)
        self.assertEqual(project.dimensions.all()[
                         1].dimension_object.milestones.all()[0].on_schedule(), False)

        project.dimensions.all()[0].dimension_object.update_value(
            7, now + timedelta(days=3))
        self.assertEqual(project.dimensions.all()[
                         1].dimension_object.milestones.all()[0].on_schedule(), True)

    def test_project_manager_dimension(self):
        d1 = ProjectManagerDimension()
        d1.save()

        person1 = Person()
        person1.first_name = 'first first'
        person1.last_name = 'first last'
        person1.save()

        person2 = Person()
        person2.first_name = 'second first'
        person2.last_name = 'second last'
        person2.save()

        d1.update_value(person1)
        d1.update_value(person2)

        person2.first_name = 'updated second first'
        person2.save()

        versions = Version.objects.get_for_object(d1)
        self.assertEqual(len(versions), 2)
        self.assertEqual(Person.objects.get(pk=versions[0].field_dict[
                         'value_id']).first_name, 'updated second first')
        self.assertEqual(Person.objects.get(pk=versions[1].field_dict[
                         'value_id']).first_name, 'first first')

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

        person1 = Person()
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
        self.assertEqual(Person.objects.get(pk=versions[1].field_dict[
                         'members'][0]).first_name, 'first first')
        self.assertEqual(Person.objects.get(pk=versions[1].field_dict[
                         'members'][1]).first_name, 'second first')

    def test_project_dependencies_dimension(self):
        d1 = ProjectDependenciesDimension()
        d1.save()

        project1 = Project()
        project1.name = 'projekti1'
        project1.save()

        project2 = Project()
        project2.name = 'projekti2'
        project2.save()

        d1.set_dependencies([project1])
        d1.set_dependencies([project1, project2])

        versions = Version.objects.get_for_object(d1)
        self.assertEqual(len(versions), 2)

        self.assertEqual(len(versions[0].field_dict['dependencies']), 2)
        self.assertEqual(versions[0].field_dict[
                         'dependencies'][0], project1.id)
        self.assertEqual(versions[0].field_dict[
                         'dependencies'][1], project2.id)

    def test_suppliers_dimension(self):
        d1 = SuppliersDimension()
        d1.save()

        supplier1 = Supplier()
        supplier1.name = 'supplier1'
        supplier1.save()

        supplier2 = Supplier()
        supplier2.name = 'supplier2'
        supplier2.save()

        d1.set_suppliers([supplier1])
        d1.set_suppliers([supplier1, supplier2])

        versions = Version.objects.get_for_object(d1)
        self.assertEqual(len(versions), 2)

        self.assertEqual(len(versions[0].field_dict['suppliers']), 2)
        self.assertEqual(Supplier.objects.get(pk=versions[0].field_dict[
                         'suppliers'][0]).name, supplier1.name)
        self.assertEqual(Supplier.objects.get(pk=versions[0].field_dict[
                         'suppliers'][1]).name, supplier2.name)
