from django.db.models import get_models, get_model

from edc_appointment.models import Appointment
from edc_registration.models import RegisteredSubject

APP_LABEL = 0
MODEL_NAME = 1


class ResaveSubject(object):
    """ Resaves all model instances for a given subject.

    for example:

        ResaveSubject(
            '062-5511-0',
            ('maikalelo_maternal','maternalconsent'),
            ('maikalelo_maternal', 'maternalvisit'),
            'maternal_visit'
            )
    """

    def __init__(self, subject_identifier, consent, visit, visit_model_attr):
        self.subject_identifier = subject_identifier
        self.visit_model = get_model(visit[APP_LABEL], visit[MODEL_NAME])
        self.visit_model_attr = visit_model_attr
        if consent:
            self.consent_model = get_model(consent[APP_LABEL], consent[MODEL_NAME])
        else:
            self.consent_model = None
        self.field_contains = '%s__appointment__registered_subject__subject_identifier' % (visit_model_attr,)
        self.resave_registered_subject()
        self.resave_consents()
        self.resave_unscheduled_and_registration()
        self.resave_appointments()
        self.resave_visits()
        self.resave_scheduled()

    def resave_registered_subject(self):
        registered_subjects = RegisteredSubject.objects.filter(subject_identifier=self.subject_identifier)
        for obj in registered_subjects:
            obj.save()
            print("saved registered_subject pk={}".format(obj.pk))

    def resave_consents(self):
        if self.consent_model:
            consents = self.consent_model.objects.filter(subject_identifier=self.subject_identifier)
            for consent in consents:
                consent.save()
                print("saved consent pk={}".format(consent.pk))

    def resave_unscheduled_and_registration(self):
        """Resaves unscheduled and other models with a key to registered subject."""
        for model in get_models():
            if getattr(model, 'registered_subject'):
                try:
                    obj = model.objects.get(registered_subject__subject_identifier=self.subject_identifier)
                    obj.save()
                    print("saved  {} pk={}".format(model._meta.model_name, obj.pk))
                except model.DoesNotExist:
                    pass

    def resave_appointments(self):
        """Resaves the appointment models instances."""
        appointments = Appointment.objects.filter(registered_subject__subject_identifier=self.subject_identifier)
        for appointment in appointments:
            appointment.save()
            print("saved appointment pk={}".format(appointment.pk))

    def resave_visits(self):
        """Resaves the visit models instances."""
        visits = self.visit_model.objects.filter(
            appointment__registered_subject__subject_identifier=self.subject_identifier)
        for visit in visits:
            visit.save()
            print("saved visit pk={}".format(visit.pk))

    def resave_scheduled(self):
        """Resaves scheduled forms, will also resave the audit record."""
        for model in get_models():
            try:
                if getattr(model, self.visit_model_attr):
                    models = model.objects.filter(**{self.field_contains: self.subject_identifier})
                    for model in models:
                        model.save()
                        print("saved {} pk={}" % (model._meta.model_name, model.pk))
            except:
                pass
