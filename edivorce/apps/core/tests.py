from django.test import TestCase
from edivorce.apps.core.models import UserResponse, Question, BceidUser
from edivorce.apps.core.utils.step_completeness import is_complete
from edivorce.apps.core.utils.question_step_mapping import question_step_mapping

# Create your tests here.
from edivorce.apps.core.utils.user_response import get_data_for_user, get_step_responses


class UserResponseTestCase(TestCase):
    fixtures = ['Question.json']

    def setUp(self):
        self.user = BceidUser.objects.create(user_guid='1234')

    def check_completeness(self, step):
        responses_dict = get_data_for_user(self.user)
        responses_dict_by_step = get_step_responses(responses_dict)
        return is_complete(responses_dict_by_step[step])

    def create_response(self, question, value):
        UserResponse.objects.create(bceid_user=self.user, question=Question.objects.get(key=question), value=value)

    def test_which_order(self):
        step = 'which_orders'

        # No response should be False
        self.assertEqual(self.check_completeness(step), False)

        # All required question
        self.create_response('want_which_orders', '["nothing"]')
        self.assertEqual(self.check_completeness(step), True)

        # Put empty response
        UserResponse.objects.filter(question_id='want_which_orders').update(value="[]")
        self.assertEqual(self.check_completeness(step), False)

    def test_your_info(self):
        step = 'your_information'

        # No response should be False
        self.assertEqual(self.check_completeness(step), False)

        # Testing required questions
        # Missing few required questions
        self.create_response('name_you', 'John Doe')
        self.create_response('last_name_before_married_you', 'Jackson')
        self.create_response('birthday_you', '11/11/1111')
        self.create_response('occupation_you', 'Plumber')

        self.assertEqual(self.check_completeness(step), False)

        # Few required questions with one checking question with hidden question not shown
        self.create_response('lived_in_bc_you', '11/11/1111')
        self.assertEqual(self.check_completeness(step), False)

        # All required questions with one checking question with hidden question not shown
        self.create_response('last_name_born_you', 'Jackson')
        self.assertEqual(self.check_completeness(step), False)

        UserResponse.objects.filter(question_id='lived_in_bc_you').update(value="Moved to B.C. on")
        self.assertEqual(self.check_completeness(step), False)

        # All required questions with one checking question with hidden question
        self.create_response('moved_to_bc_date_you', '12/12/1212')
        self.assertEqual(self.check_completeness(step), False)

        # All required questions with two checking question with one hidden and one shown
        self.create_response('any_other_name_you', 'NO')
        self.assertEqual(self.check_completeness(step), True)

        # All required questions with two checking question with one hidden question missing
        UserResponse.objects.filter(question_id='any_other_name_you').update(value="YES")
        self.assertEqual(self.check_completeness(step), False)

        # All required questions with all checking question with all hidden questions
        self.create_response('other_name_you', '[["also known as","Smith"]]')
        self.assertEqual(self.check_completeness(step), True)

        # Put empty response
        UserResponse.objects.filter(question_id='other_name_you').update(value='[["",""]]')
        self.assertEqual(self.check_completeness(step), False)

    def test_your_spouse(self):
        step = 'your_spouse'

        # No response should be False
        self.assertEqual(self.check_completeness(step), False)

        # Testing required questions
        # Missing few required questions
        self.create_response('name_spouse', 'John Doe')
        self.create_response('last_name_before_married_spouse', 'Jackson')
        self.create_response('birthday_spouse', '11/11/1111')
        self.create_response('occupation_spouse', 'Electrician')

        self.assertEqual(self.check_completeness(step), False)

        # Few required questions with one checking question with hidden question not shown
        self.create_response('any_other_name_spouse', 'NO')
        self.assertEqual(self.check_completeness(step), False)

        # All required questions with one checking question with hidden question not shown
        self.create_response('last_name_born_spouse', 'Jackson')
        self.assertEqual(self.check_completeness(step), False)

        # All required questions with one checking question with hidden question missing
        UserResponse.objects.filter(question_id='any_other_name_spouse').update(value="YES")
        self.assertEqual(self.check_completeness(step), False)

        # All required questions with one checking question with hidden question
        self.create_response('lived_in_bc_spouse', 'Since birth')
        self.assertEqual(self.check_completeness(step), False)

        # All required questions with two checking question with one hidden and one shown
        self.create_response('other_name_spouse', '[["also known as","Smith"]]')
        self.assertEqual(self.check_completeness(step), True)

        # All required questions with two checking question with one hidden question missing
        UserResponse.objects.filter(question_id='lived_in_bc_spouse').update(value="Moved to B.C. on")
        self.assertEqual(self.check_completeness(step), False)

        # All required questions with all checking question with all hidden questions
        self.create_response('moved_to_bc_date_spouse', '12/12/1212')
        self.assertEqual(self.check_completeness(step), True)

        # Put empty response
        UserResponse.objects.filter(question_id='name_spouse').update(value="")
        self.assertEqual(self.check_completeness(step), False)

        # Put empty response
        UserResponse.objects.filter(question_id='other_name_spouse').update(value='[["",""]]')
        self.assertEqual(self.check_completeness(step), False)

    def test_your_marriage(self):
        step = 'your_marriage'

        # No response should be False
        self.assertEqual(self.check_completeness(step), False)

        # Some required questions
        self.create_response('when_were_you_live_married_like', '12/12/2007')
        self.assertEqual(self.check_completeness(step), False)

        self.create_response('when_were_you_married', '12/12/2008')
        self.assertEqual(self.check_completeness(step), False)

        self.create_response('marital_status_before_you', 'Never married')
        self.assertEqual(self.check_completeness(step), False)

        self.create_response('marital_status_before_spouse', 'Widowed')
        self.assertEqual(self.check_completeness(step), False)

        self.create_response('where_were_you_married_city', 'Vancouver')
        self.assertEqual(self.check_completeness(step), False)

        self.create_response('where_were_you_married_prov', 'BC')
        self.assertEqual(self.check_completeness(step), False)

        # All required questions
        self.create_response('where_were_you_married_country', 'Canada')
        self.assertEqual(self.check_completeness(step), True)

        # All required questions but missing conditional question
        UserResponse.objects.filter(question_id='where_were_you_married_country').update(value="Other")
        self.assertEqual(self.check_completeness(step), False)

        # All required questions
        self.create_response('where_were_you_married_other_country', 'Peru')
        self.assertEqual(self.check_completeness(step), True)

    def test_your_separation(self):
        step = 'your_separation'
        # No response should be False
        self.assertEqual(self.check_completeness(step), False)

        # All required question
        self.create_response('no_reconciliation_possible', 'I agree')
        self.assertEqual(self.check_completeness(step), False)

        # Put empty response
        UserResponse.objects.filter(question_id='no_reconciliation_possible').update(value="")
        self.assertEqual(self.check_completeness(step), False)

    def test_spousal_support(self):
        step = 'spousal_support'

        # No response should be False
        self.assertEqual(self.check_completeness(step), False)

        # One required question
        self.create_response('spouse_support_details', 'I will support you')
        self.assertEqual(self.check_completeness(step), False)

        # Two required questions
        self.create_response('spouse_support_act', 'Family Law')
        self.assertEqual(self.check_completeness(step), True)

        # Remove first added required response to test the second required question
        UserResponse.objects.get(question_id='spouse_support_details').delete()

        self.assertEqual(self.check_completeness(step), False)

        # Put empty response
        UserResponse.objects.filter(question_id='spouse_support_details').update(value="")

        self.assertEqual(self.check_completeness(step), False)

    def test_property_and_debt(self):
        step = 'property_and_debt'

        # No response should be False
        self.assertEqual(self.check_completeness(step), False)

        # All required question with no hidden shown
        self.create_response('deal_with_property_debt', 'Equal division')

        self.assertEqual(self.check_completeness(step), True)

        # All required question with hidden shown but no response
        UserResponse.objects.filter(question_id='deal_with_property_debt').update(value="Unequal division")

        self.assertEqual(self.check_completeness(step), False)

        # Only one required question with hidden shown and answered
        self.create_response('how_to_divide_property_debt', 'Do not divide them')

        self.assertEqual(self.check_completeness(step), True)

        # All required question with optional fields
        self.create_response('other_property_claims', 'Want these property claims')
        self.assertEqual(self.check_completeness(step), True)

    def test_other_orders(self):
        step = 'other_orders'

        # No response should be False
        self.assertEqual(self.check_completeness(step), False)

        # All required question
        self.create_response('name_change_you', 'NO')
        self.assertEqual(self.check_completeness(step), False)

        self.create_response('name_change_spouse', 'NO')
        self.create_response('other_orders_detail', 'I want more orders')

        self.assertEqual(self.check_completeness(step), True)

        # make incomplete
        UserResponse.objects.filter(question_id='name_change_spouse').update(value="YES")
        self.assertEqual(self.check_completeness(step), False)

        self.create_response('name_change_spouse_fullname', 'new name')
        self.assertEqual(self.check_completeness(step), True)

        # Put empty response
        UserResponse.objects.filter(question_id='other_orders_detail').update(value="")
        self.assertEqual(self.check_completeness(step), True)

    def test_other_questions(self):
        step = 'other_questions'

        # No response should be False
        self.assertEqual(self.check_completeness(step), False)

        # Some required question
        self.create_response('address_to_send_official_document_street_you', '123 Cambie st')
        self.assertEqual(self.check_completeness(step), False)

        self.create_response('address_to_send_official_document_city_you', 'Vancouver')
        self.assertEqual(self.check_completeness(step), False)

        self.create_response('address_to_send_official_document_prov_you', 'BC')
        self.assertEqual(self.check_completeness(step), False)

        self.create_response('address_to_send_official_document_country_you', 'Canada')
        self.assertEqual(self.check_completeness(step), False)

        # All required questions for you
        self.create_response('address_to_send_official_document_postal_code_you', 'Canada')
        self.assertEqual(self.check_completeness(step), False)

        # One required question for spouse
        self.create_response('address_to_send_official_document_street_spouse', '123 Cambie st')
        self.assertEqual(self.check_completeness(step), False)

        # Two required question for spouse
        self.create_response('address_to_send_official_document_city_spouse', 'Vancouver')
        self.assertEqual(self.check_completeness(step), False)

        # Three required question for spouse
        self.create_response('address_to_send_official_document_prov_spouse', 'BC')
        self.assertEqual(self.check_completeness(step), False)

        # Four required question for spouse
        self.create_response('address_to_send_official_document_country_spouse', 'Canada')
        self.assertEqual(self.check_completeness(step), False)

        # All required questions
        self.create_response('divorce_take_effect_on', 'the 31st day after the date of this order')
        self.assertEqual(self.check_completeness(step), True)

        # Missing conditional required question
        UserResponse.objects.filter(question_id='divorce_take_effect_on').update(value="specific date")
        self.assertEqual(self.check_completeness(step), False)

        # All required questions
        self.create_response('divorce_take_effect_on_specific_date', '12/12/2018')
        self.assertEqual(self.check_completeness(step), True)

        # All required questions for spouse and you
        self.create_response('address_to_send_official_document_postal_code_spouse', 'Canada')

        self.assertEqual(self.check_completeness(step), True)

        # All required questions for spouse and you with empty email(optional so still true)
        self.create_response('address_to_send_official_document_email_you', 'a@example.com')
        self.assertEqual(self.check_completeness(step), True)

        # Testing other country missing
        UserResponse.objects.filter(question_id='address_to_send_official_document_country_spouse').update(value="Other")
        self.assertEqual(self.check_completeness(step), False)

        # All required questions
        self.create_response('address_to_send_official_document_other_country_spouse', 'Mexico')
        self.assertEqual(self.check_completeness(step), True)

        # Set Specific date on to empty
        UserResponse.objects.filter(question_id='divorce_take_effect_on_specific_date').update(value="")
        self.assertEqual(self.check_completeness(step), False)

    def test_filing_locations(self):
        step = 'filing_locations'

        # No response should be False
        self.assertEqual(self.check_completeness(step), False)

        # All required question
        self.create_response('court_registry_for_filing', 'Vancouver')
        self.assertEqual(self.check_completeness(step), True)

        # Put empty response
        UserResponse.objects.filter(question_id='court_registry_for_filing').update(value="")
        self.assertEqual(self.check_completeness(step), False)
