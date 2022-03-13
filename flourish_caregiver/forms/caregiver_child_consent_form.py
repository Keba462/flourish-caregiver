from functools import partialmethod
from charset_normalizer import from_path

from django import forms
from django.apps import apps as django_apps

from ..models import CaregiverChildConsent
from .form_mixins import SubjectModelFormMixin

from flourish_form_validations.form_validators import CaregiverChildConsentFormValidator
from edc_constants.constants import MALE, FEMALE


class CaregiverChildConsentForm(SubjectModelFormMixin):
    # form_validator_cls = CaregiverChildConsentFormValidator

    child_dataset_model = 'flourish_child.childdataset'

    @property
    def child_dataset_cls(self):
        return django_apps.get_model(self.child_dataset_model)

    subject_identifier = forms.CharField(
        label='Subject Identifier',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        required=False)

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)

        # # fields alread initialized in the super
        study_child_identifier = self.initial.get('study_child_identifier', None)
        gender = self.initial.get('gender', None)
        child_dob = self.initial.get('child_dob', None)

        # # if and only if the above fields exist, make the field readonly
        # # or else make the fields editable
        if study_child_identifier:
            self.fields['study_child_identifier'].disabled = True
        if gender:
            self.fields['gender'].disabled = True
        if child_dob:
            self.fields['child_dob'] = forms.CharField(initial=self.initial['child_dob'], )
            self.fields['child_dob'].disabled = True

        screening_identifier = kwargs.get('screening_identifier', None)
        setattr(CaregiverChildConsentFormValidator, 'screening', screening_identifier)

        instance = getattr(self, 'instance', None)
        subject_identifier = instance.subject_identifier if instance else None
        if subject_identifier and not self.screening_preg_exists(instance=instance):
            for key in self.fields.keys():
                self.fields[key].disabled = True
        self.errors



    def has_changed(self):
        return True

    def screening_preg_exists(self, instance=None):
        preg_women_screening_cls = django_apps.get_model(
            'flourish_caregiver.screeningpregwomen')

        try:
            preg_women_screening_cls.objects.get(
                screening_identifier=instance.subject_consent.screening_identifier)
        except preg_women_screening_cls.DoesNotExist:
            return False
        else:
            return True

    # def get_formset(self, request, obj=None, **kwargs):
    #     initial = []
    #     study_maternal_id = request.GET.get('study_maternal_identifier')
    #     if study_maternal_id:
    #         child_datasets = self.child_dataset_cls.objects.filter(
    #             study_maternal_identifier=study_maternal_id)
    #         genders = {'Male': MALE, 'Female': FEMALE}
    #         if obj:
    #             child_datasets = self.get_difference(child_datasets, obj)

    #         for child in child_datasets:
    #             initial.append({
    #                 'study_child_identifier': child.study_child_identifier,
    #                 'gender': genders.get(child.infant_sex),
    #                 'child_dob': child.dob
    #             })

    #     formset = super().get_formset(request, obj=obj, **kwargs)
    #     formset.__init__ = partialmethod(formset.__init__, initial=initial)
    #     return formset

    # def get_extra(self, request, obj=None, **kwargs):
    #     extra = super().get_extra(request, obj, **kwargs)
    #     study_maternal_id = request.GET.get('study_maternal_identifier')
    #     if study_maternal_id:
    #         child_datasets = self.child_dataset_cls.objects.filter(
    #             study_maternal_identifier=study_maternal_id)
    #         if not obj:
    #             child_count = child_datasets.count()
    #             extra = child_count
    #         else:
    #             extra = len(self.get_difference(child_datasets, obj))
    #     return extra

    # def get_difference(self, model_objs, obj=None):
    #     cc_ids = obj.caregiverchildconsent_set.values_list(
    #         'study_child_identifier', flat=True)
    #     return [x for x in model_objs if x.study_child_identifier not in cc_ids]

    class Meta:
        model = CaregiverChildConsent
        fields = '__all__'
