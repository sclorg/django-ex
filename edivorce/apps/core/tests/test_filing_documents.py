from django.test import TestCase

from edivorce.apps.core.models import BceidUser, Document, UserResponse
from edivorce.apps.core.utils.efiling_documents import forms_to_file
from edivorce.apps.core.utils.user_response import get_data_for_user


class FilingLogic(TestCase):
    fixtures = ['Question.json']

    def setUp(self):
        self.user = BceidUser.objects.create(user_guid='1234')
        self.create_response('how_to_file', 'Online')

    def create_response(self, question, value):
        response, _ = UserResponse.objects.get_or_create(bceid_user=self.user, question_id=question)
        response.value = value
        response.save()

    @property
    def questions_dict(self):
        return get_data_for_user(self.user)

    def test_initial_forms_to_file_in_person(self):
        def assert_package_1_needed():
            self.create_response('original_marriage_certificate', 'NO')
            self.create_response('where_were_you_married_country', 'Canada')
            self.create_response('where_were_you_married_prov', 'BC')

            # Base forms required
            uploaded, generated = forms_to_file(self.questions_dict, initial=True)

            self.assertEqual(len(uploaded), 1)
            self.assertIn({'doc_type': doc_type("joint divorce proceedings"), 'party_code': 0}, uploaded)

            self.assertEqual(len(generated), 1)
            self.assertIn({'doc_type': doc_type("notice of joint family claim"), 'form_number': 1}, generated)

            # Marriage certificate required
            self.create_response('original_marriage_certificate', 'YES')
            uploaded, generated = forms_to_file(self.questions_dict, initial=True)

            self.assertEqual(len(uploaded), 2)
            self.assertIn({'doc_type': doc_type("proof of marriage"), 'party_code': 0}, uploaded)

            # Affidavit of translation required
            self.create_response('where_were_you_married_prov', 'QC')
            uploaded, generated = forms_to_file(self.questions_dict, initial=True)

            self.assertEqual(len(uploaded), 3)
            self.assertIn({'doc_type': doc_type("affidavit of translation"), 'party_code': 0}, uploaded)

        self.create_response('how_to_sign', 'Together')
        self.create_response('signing_location', 'In-person')

        assert_package_1_needed()

        self.create_response('how_to_sign', 'Separately')
        self.create_response('signing_location_you', 'In-person')
        self.create_response('signing_location_spouse', 'In-person')

        assert_package_1_needed()

        self.create_response('how_to_sign', 'Separately')
        self.create_response('signing_location_you', 'In-person')
        self.create_response('signing_location_spouse', 'Virtual')

        assert_package_1_needed()

    def test_initial_forms_to_file_both_virtual(self):
        def assert_package_1_2_3_needed(with_efss_spouse=False):
            # No conditional forms
            self.create_response('children_of_marriage', 'NO')
            self.create_response('name_change_you', 'NO')
            self.create_response('name_change_spouse', 'NO')
            self.create_response('original_marriage_certificate', 'NO')
            self.create_response('where_were_you_married_country', 'Canada')
            self.create_response('where_were_you_married_prov', 'BC')

            uploaded, generated = forms_to_file(self.questions_dict, initial=True)

            doc_count = len(uploaded)
            if with_efss_spouse:
                self.assertEqual(doc_count, 4)
            else:
                self.assertEqual(doc_count, 3)
            self.assertIn({'doc_type': doc_type("draft final order"), 'party_code': 0}, uploaded)
            self.assertIn({'doc_type': doc_type("joint divorce proceedings"), 'party_code': 0}, uploaded)
            self.assertIn({'doc_type': doc_type("electronic filing"), 'party_code': 1}, uploaded)
            if with_efss_spouse:
                self.assertIn({'doc_type': doc_type("electronic filing"), 'party_code': 2}, uploaded)

            self.assertEqual(len(generated), 3)
            self.assertIn({'doc_type': doc_type("notice of joint family claim"), 'form_number': 1}, generated)
            self.assertIn({'doc_type': doc_type("requisition form"), 'form_number': 35}, generated)
            self.assertIn({'doc_type': doc_type("certificate of pleadings"), 'form_number': 36}, generated)

            # Conditional forms
            self.create_response('children_of_marriage', 'YES')
            self.create_response('has_children_under_19', 'YES')
            uploaded, generated = forms_to_file(self.questions_dict, initial=True)
            self.assertEqual(len(uploaded), doc_count + 1)
            self.assertIn({'doc_type': doc_type("agreement as to annual income"), 'party_code': 0}, uploaded)

            self.create_response('want_which_orders', '["Other orders"]')
            self.create_response('name_change_you', 'YES')
            uploaded, generated = forms_to_file(self.questions_dict, initial=True)
            self.assertEqual(len(uploaded), doc_count + 2)
            self.assertIn({'doc_type': doc_type("identification of applicant"), 'party_code': 1}, uploaded)

            self.create_response('name_change_spouse', 'YES')
            uploaded, generated = forms_to_file(self.questions_dict, initial=True)
            self.assertEqual(len(uploaded), doc_count + 3)
            self.assertIn({'doc_type': doc_type("identification of applicant"), 'party_code': 2}, uploaded)

            # Marriage certificate required
            self.create_response('original_marriage_certificate', 'YES')
            uploaded, generated = forms_to_file(self.questions_dict, initial=True)

            self.assertEqual(len(uploaded), doc_count + 4)
            self.assertIn({'doc_type': doc_type("proof of marriage"), 'party_code': 0}, uploaded)

            # Affidavit of translation + F96 required
            self.create_response('where_were_you_married_prov', 'QC')
            uploaded, generated = forms_to_file(self.questions_dict, initial=True)

            self.assertEqual(len(uploaded), doc_count + 5)
            self.assertIn({'doc_type': doc_type("affidavit of translation"), 'party_code': 0}, uploaded)

        self.create_response('how_to_sign', 'Together')
        self.create_response('signing_location', 'Virtual')

        assert_package_1_2_3_needed()

        self.create_response('how_to_sign', 'Separately')
        self.create_response('signing_location_you', 'Virtual')
        self.create_response('signing_location_spouse', 'Virtual')

        assert_package_1_2_3_needed(with_efss_spouse=True)

    def test_initial_forms_to_file_you_virtual_spouse_in_person(self):
        def assert_package_1_2_needed():
            # No conditional forms
            self.create_response('original_marriage_certificate', 'NO')
            self.create_response('where_were_you_married_country', 'Canada')
            self.create_response('where_were_you_married_prov', 'BC')
            uploaded, generated = forms_to_file(self.questions_dict, initial=True)

            self.assertEqual(len(uploaded), 3)
            self.assertIn({'doc_type': doc_type("electronic filing"), 'party_code': 1}, uploaded)
            self.assertIn({'doc_type': doc_type("draft final order"), 'party_code': 0}, uploaded)
            self.assertIn({'doc_type': doc_type("joint divorce proceedings"), 'party_code': 0}, uploaded)

            self.assertEqual(len(generated), 3)
            self.assertIn({'doc_type': doc_type("notice of joint family claim"), 'form_number': 1}, generated)
            self.assertIn({'doc_type': doc_type("requisition form"), 'form_number': 35}, generated)
            self.assertIn({'doc_type': doc_type("certificate of pleadings"), 'form_number': 36}, generated)

            # Conditional forms
            self.create_response('children_of_marriage', 'YES')
            self.create_response('has_children_under_19', 'YES')
            uploaded, generated = forms_to_file(self.questions_dict, initial=True)
            self.assertEqual(len(uploaded), 4)
            self.assertIn({'doc_type': doc_type("agreement as to annual income"), 'party_code': 0}, uploaded)

            self.create_response('want_which_orders', '["Other orders"]')
            self.create_response('name_change_you', 'YES')
            self.create_response('name_change_spouse', 'YES')
            uploaded, generated = forms_to_file(self.questions_dict, initial=True)
            self.assertEqual(len(uploaded), 5)
            self.assertIn({'doc_type': doc_type("identification of applicant"), 'party_code': 1}, uploaded)

            # Marriage certificate required
            self.create_response('original_marriage_certificate', 'YES')
            uploaded, generated = forms_to_file(self.questions_dict, initial=True)

            self.assertEqual(len(uploaded), 6)
            self.assertIn({'doc_type': doc_type("proof of marriage"), 'party_code': 0}, uploaded)

            # Affidavit of translation required
            self.create_response('where_were_you_married_prov', 'QC')
            uploaded, generated = forms_to_file(self.questions_dict, initial=True)

            self.assertEqual(len(uploaded), 7)
            self.assertIn({'doc_type': doc_type("affidavit of translation"), 'party_code': 0}, uploaded)

        self.create_response('how_to_sign', 'Separately')
        self.create_response('signing_location_you', 'Virtual')
        self.create_response('signing_location_spouse', 'In-person')

        assert_package_1_2_needed()

    def test_final_forms_to_file_together_virtually(self):
        self.create_response('how_to_sign', 'Together')
        self.create_response('signing_location', 'Virtual')
        self.create_response('children_of_marriage', 'NO')

        uploaded, generated = forms_to_file(self.questions_dict, initial=False)

        self.assertEqual(len(uploaded), 1)
        self.assertIn({'doc_type': doc_type("desk order divorce form"), 'party_code': 0}, uploaded)

        self.assertEqual(len(generated), 0)
        self.create_response('children_of_marriage', 'YES')
        self.create_response('has_children_under_19', 'YES')

        uploaded, generated = forms_to_file(self.questions_dict, initial=False)

        self.assertEqual(len(uploaded), 2)
        self.assertIn({'doc_type': doc_type("child support affidavit"), 'party_code': 0}, uploaded)

    def test_final_forms_to_file_separately_virtually(self):
        self.create_response('how_to_sign', 'Separately')
        self.create_response('signing_location_you', 'Virtual')
        self.create_response('signing_location_spouse', 'Virtual')
        self.create_response('children_of_marriage', 'NO')

        uploaded, generated = forms_to_file(self.questions_dict, initial=False)

        self.assertEqual(len(uploaded), 2)
        self.assertIn({'doc_type': doc_type("desk order divorce form"), 'party_code': 1}, uploaded)
        self.assertIn({'doc_type': doc_type("desk order divorce form"), 'party_code': 2}, uploaded)

        self.assertEqual(len(generated), 0)
        self.create_response('children_of_marriage', 'YES')
        self.create_response('has_children_under_19', 'YES')

        uploaded, generated = forms_to_file(self.questions_dict, initial=False)

        self.assertEqual(len(uploaded), 4)
        self.assertIn({'doc_type': doc_type("child support affidavit"), 'party_code': 1}, uploaded)
        self.assertIn({'doc_type': doc_type("child support affidavit"), 'party_code': 2}, uploaded)

    def test_final_forms_to_file_in_person(self):
        self.create_response('how_to_sign', 'Together')
        self.create_response('signing_location', 'In-person')

        # No conditional forms
        self.create_response('children_of_marriage', 'NO')
        uploaded, generated = forms_to_file(self.questions_dict, initial=False)

        self.assertEqual(len(uploaded), 4)
        self.assertIn({'doc_type': doc_type("electronic filing"), 'party_code': 1}, uploaded)
        self.assertIn({'doc_type': doc_type("electronic filing"), 'party_code': 2}, uploaded)
        self.assertIn({'doc_type': doc_type("desk order divorce form"), 'party_code': 0}, uploaded)
        self.assertIn({'doc_type': doc_type("draft final order"), 'party_code': 0}, uploaded)

        self.assertEqual(len(generated), 2)
        self.assertIn({'doc_type': doc_type("requisition form"), 'form_number': 35}, generated)
        self.assertIn({'doc_type': doc_type("certificate of pleadings"), 'form_number': 36}, generated)

        # Conditional forms
        self.create_response('children_of_marriage', 'YES')
        self.create_response('has_children_under_19', 'YES')
        uploaded, generated = forms_to_file(self.questions_dict, initial=False)
        self.assertEqual(len(uploaded), 6)
        self.assertIn({'doc_type': doc_type("child support affidavit"), 'party_code': 0}, uploaded)
        self.assertIn({'doc_type': doc_type("agreement as to annual income"), 'party_code': 0}, uploaded)

        self.create_response('want_which_orders', '["Other orders"]')
        self.create_response('name_change_you', 'YES')
        uploaded, generated = forms_to_file(self.questions_dict, initial=False)
        self.assertEqual(len(uploaded), 7)
        self.assertIn({'doc_type': doc_type("identification of applicant"), 'party_code': 1}, uploaded)

        self.create_response('name_change_spouse', 'YES')
        uploaded, generated = forms_to_file(self.questions_dict, initial=False)
        self.assertEqual(len(uploaded), 8)
        self.assertIn({'doc_type': doc_type("identification of applicant"), 'party_code': 2}, uploaded)


def doc_type(text):
    for doc_type, name in Document.form_types.items():
        if text.lower() in name.lower():
            return doc_type
    raise ValueError(f"Couldn't find doc with name that contains '{text}'")
