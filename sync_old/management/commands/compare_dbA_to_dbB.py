from django.db.models import Count, get_models, get_app
from django.core.management.base import BaseCommand
from edc.subject.lab_tracker.classes import site_lab_tracker
from ...models import IncomingTransaction

site_lab_tracker.autodiscover()


class Command(BaseCommand):
    '''arguments
        app_name: name of the app to compare its tables.
        dbA: the smaller database to compare to the larger databas.e
        dbB: The larger database which is a combination of smaller databases.
        output_file
    '''
    args = ()
    help = 'Ensure records in table X in db A all match to records in table X of db B.'

    def handle(self, *args, **options):
        if len(args) != 4:
            print 'missing arguments. requires app_name databaseA databaseB absolute_path_to_output_file'
            return
        app_name = args[0]
        dbA = args[1]
        dbB = args[2]
        output_file = args[3]
        self.compare_databases(app_name, dbA, dbB, output_file)

    def compare_databases(self, app_name, dbA, dbB, output_file):
        #
        model_classes = get_models(get_app(app_name))
        model_classes = [model for model in model_classes if model._meta.module_name.find('audit') == -1]
        out_file = open(output_file, 'w')
        for model_class in model_classes:
            model_instancesA = model_class.objects.using(dbA).all()
            model_instancesB = model_class.objects.using(dbB).all()
            print '{0}={1} in {2} and {3} in {4}'.format(model_class, model_instancesA.count(), dbA, model_instancesB.count(), dbB)
            out_file.write('{0}={1} in {2} and {3} in {4}'.format(model_class, model_instancesA.count(), dbA, model_instancesB.count(), dbB))
            out_file.write('\n')
            out_file.write('\n')
            fields = model_class._meta.fields
            fields = [f for f in fields if f.name not in ['hostname_created', 'user_modified', 'user_created', 'revision', 'modified', 'hostname_modified', 'created', 'study_site',
                                                           'visit_definition', 'survey', 'distance_from_target', 'plot_log', 'site']]
            for model_instanceA in model_instancesA:
                try:
                    model_instanceB = model_instancesB.get(id=model_instanceA.id)
                except model_class.DoesNotExist:
                    out_file.write('Could not locate model {0} of id {1} from DB {2} in DB {3}. Date Modified={4}'.format(model_class, model_instanceA.id, dbA, dbB, model_instanceA.modified))
                    out_file.write('\n')
                    out_file.write('\n')
                    continue
                for field in fields:
                    fieldA = getattr(model_instanceA, field.name)
                    fieldB = getattr(model_instanceB, field.name)
                    if fieldA != fieldB:
                        print 'Field {0} for model {1} of id {2} in {3} mismatched that in {4}. Got {5} for {6} and {7} for {8}. Date modified={9}'.format(
                                     field.name, model_class, model_instanceA.id, dbA, dbB, getattr(model_instanceA, field.name), dbA, getattr(model_instanceB, field.name), dbB, model_instanceA.modified)
                        out_file.write('Field {0} for model {1} of id {2} in {3} mismatched that in {4}. Got {5} for {6} and {7} for {8}. Date modified={9}'.format(
                                     field.name, model_class, model_instanceA.id, dbA, dbB, getattr(model_instanceA, field.name), dbA, getattr(model_instanceB, field.name), dbB, model_instanceA.modified))
                        out_file.write('\n')
                        out_file.write('\n')
        out_file.close()
