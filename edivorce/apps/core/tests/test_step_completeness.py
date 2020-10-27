import json

from django.test import TestCase
from edivorce.apps.core.models import UserResponse, Question, BceidUser
from edivorce.apps.core.utils.derived import get_derived_data
from edivorce.apps.core.utils.step_completeness import Status, get_error_dict, get_step_completeness, is_complete

from edivorce.apps.core.utils.user_response import get_data_for_user, get_step_responses


class StepCompletenessTestCase(TestCase):
    fixtures = ['Question.json']

    def setUp(self):
        self.user = BceidUser.objects.create(user_guid='1234')

    def check_completeness(self, step):
        responses_dict = get_data_for_user(self.user)
        responses_dict_by_step = get_step_responses(responses_dict)
        return is_complete(responses_dict_by_step[step])

    def check_step_status(self, step):
        responses_dict = get_data_for_user(self.user)
        responses_dict_by_step = get_step_responses(responses_dict)
        step_completeness = get_step_completeness(responses_dict_by_step)
        return step_completeness[step]

    def create_response(self, question, value):
        response, _ = UserResponse.objects.get_or_create(bceid_user=self.user, question_id=question)
        response.value = value
        response.save()

    def test_prequalification(self):
        step = 'prequalification'

        # No response should be False
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.NOT_STARTED)

        # Testing required questions
        # Missing few required questions
        self.create_response('married_marriage_like', 'Legally married')
        self.create_response('lived_in_bc', 'YES')
        self.create_response('lived_in_bc_at_least_year', 'YES')
        self.create_response('separation_date', '11/11/1111')
        self.create_response('try_reconcile_after_separated', 'NO')
        self.create_response('children_of_marriage', 'NO')
        self.create_response('original_marriage_certificate', 'YES')
        self.create_response('marriage_certificate_in_english', 'YES')

        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.STARTED)

        # All required questions with one checking question with hidden question not shown
        self.create_response('divorce_reason', 'live separate')
        self.assertEqual(self.check_completeness(step), True)
        self.assertEqual(self.check_step_status(step), Status.COMPLETED)

        # Reconciliation
        UserResponse.objects.filter(question_id='try_reconcile_after_separated').update(value="YES")
        self.assertEqual(self.check_completeness(step), False)
        self.create_response('reconciliation_period', '[("11/11/2011","12/11/2011")]')
        self.assertEqual(self.check_completeness(step), True)

        # Children
        UserResponse.objects.filter(question_id='children_of_marriage').update(value="YES")
        self.assertEqual(self.check_completeness(step), False)
        self.create_response('has_children_under_19', 'NO')
        self.create_response('has_children_over_19', 'NO')
        self.assertEqual(self.check_completeness(step), True)

        UserResponse.objects.filter(question_id='has_children_under_19').update(value="YES")
        self.assertEqual(self.check_completeness(step), False)
        self.create_response('children_live_with_others', 'NO')
        self.assertEqual(self.check_completeness(step), True)

        UserResponse.objects.filter(question_id='has_children_over_19').update(value="YES")
        self.assertEqual(self.check_completeness(step), False)
        self.create_response('children_financial_support', '["NO"]')
        self.assertEqual(self.check_completeness(step), True)

        # Marriage certificate
        UserResponse.objects.filter(question_id='original_marriage_certificate').update(value="NO")
        self.assertEqual(self.check_completeness(step), False)
        self.create_response('provide_certificate_later', 'YES')
        self.assertEqual(self.check_completeness(step), False)
        self.create_response('provide_certificate_later_reason', 'Because')
        self.assertEqual(self.check_completeness(step), True)

        UserResponse.objects.filter(question_id='provide_certificate_later').update(value="NO")
        self.assertEqual(self.check_completeness(step), False)
        self.create_response('not_provide_certificate_reason', 'Because')
        self.assertEqual(self.check_completeness(step), True)

    def test_which_order(self):
        step = 'which_orders'

        # No response should be False
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.NOT_STARTED)

        # Empty response
        self.create_response('want_which_orders', '[]')
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.NOT_STARTED)

        # Divorce order is required
        self.create_response('want_which_orders', '["Child support"]')
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.STARTED)

        self.create_response('want_which_orders', '["A legal end to the marriage"]')
        self.assertEqual(self.check_completeness(step), True)
        self.assertEqual(self.check_step_status(step), Status.COMPLETED)

    def test_your_info(self):
        step = 'your_information'

        # No response should be False
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.NOT_STARTED)

        # Testing required questions
        # Missing few required questions
        self.create_response('last_name_you', 'Doe')
        self.create_response('given_name_1_you', 'John')
        self.create_response('last_name_before_married_you', 'Jackson')
        self.create_response('birthday_you', '11/11/1111')
        self.create_response('occupation_you', 'Plumber')
        self.assertEqual(self.check_step_status(step), Status.STARTED)

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
        self.assertEqual(self.check_step_status(step), Status.COMPLETED)

        # All required questions with two checking question with one hidden question missing
        UserResponse.objects.filter(question_id='any_other_name_you').update(value="YES")
        self.assertEqual(self.check_completeness(step), False)

        # All required questions with all checking question with all hidden questions
        self.create_response('other_name_you', '[["also known as","Smith","James","Jerry","Joseph"]]')
        self.assertEqual(self.check_completeness(step), True)

        # Put empty response
        UserResponse.objects.filter(question_id='other_name_you').update(value='[["","","","",""]]')
        self.assertEqual(self.check_completeness(step), False)

    def test_your_spouse(self):
        step = 'your_spouse'

        # No response should be False
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.NOT_STARTED)

        # Testing required questions
        # Missing few required questions
        self.create_response('last_name_spouse', 'Doe')
        self.create_response('given_name_1_spouse', 'John')
        self.create_response('last_name_before_married_spouse', 'Jackson')
        self.create_response('birthday_spouse', '11/11/1111')
        self.create_response('occupation_spouse', 'Electrician')

        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.STARTED)

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
        self.create_response('other_name_spouse', '[["also known as","Smith","James","Jerry","Joseph"]]')
        self.assertEqual(self.check_completeness(step), True)
        self.assertEqual(self.check_step_status(step), Status.COMPLETED)

        # All required questions with two checking question with one hidden question missing
        UserResponse.objects.filter(question_id='lived_in_bc_spouse').update(value="Moved to B.C. on")
        self.assertEqual(self.check_completeness(step), False)

        # All required questions with all checking question with all hidden questions
        self.create_response('moved_to_bc_date_spouse', '12/12/1212')
        self.assertEqual(self.check_completeness(step), True)

        # Put empty response
        UserResponse.objects.filter(question_id='last_name_spouse').update(value="")
        self.assertEqual(self.check_completeness(step), False)

        # Put empty response
        UserResponse.objects.filter(question_id='other_name_spouse').update(value='[["","","","",""]]')
        self.assertEqual(self.check_completeness(step), False)

    def test_your_marriage(self):
        step = 'your_marriage'

        # No response should be False
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.NOT_STARTED)

        # Some required questions
        self.create_response('when_were_you_live_married_like', '12/12/2007')
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.STARTED)

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
        self.assertEqual(self.check_step_status(step), Status.COMPLETED)

    def test_your_separation(self):
        step = 'your_separation'
        # No response should be False
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.NOT_STARTED)

        # One required question
        self.create_response('no_reconciliation_possible', 'I agree')
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.STARTED)

        # All required question
        self.create_response('no_collusion', 'I agree')
        self.assertEqual(self.check_completeness(step), True)
        self.assertEqual(self.check_step_status(step), Status.COMPLETED)

        # Put empty response
        UserResponse.objects.filter(question_id='no_reconciliation_possible').update(value="")
        self.assertEqual(self.check_completeness(step), False)

    def test_spousal_support(self):
        step = 'spousal_support'

        # Step not required if spousal support not wanted
        self.assertEqual(self.check_completeness(step), True)
        self.assertEqual(self.check_step_status(step), Status.HIDDEN)

        # No response should be False
        self.create_response('want_which_orders', '["Spousal support"]')
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.NOT_STARTED)

        # One required question
        self.create_response('spouse_support_details', 'I will support you')
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.STARTED)

        # Two required questions
        self.create_response('spouse_support_act', 'Family Law')
        self.assertEqual(self.check_completeness(step), True)
        self.assertEqual(self.check_step_status(step), Status.COMPLETED)

        # Remove first added required response to test the second required question
        UserResponse.objects.get(question_id='spouse_support_details').delete()
        self.assertEqual(self.check_completeness(step), False)

        # Empty response doesn't count as answered
        UserResponse.objects.filter(question_id='spouse_support_details').update(value="")
        self.assertEqual(self.check_completeness(step), False)

    def test_property_and_debt(self):
        step = 'property_and_debt'

        # Step not required if property and debt orders not wanted
        self.assertEqual(self.check_completeness(step), True)
        self.assertEqual(self.check_step_status(step), Status.HIDDEN)

        # No response should be False
        self.create_response('want_which_orders', '["Division of property and debts"]')
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.NOT_STARTED)

        # All required question with no hidden shown
        self.create_response('deal_with_property_debt', 'Equal division')
        self.assertEqual(self.check_completeness(step), True)

        # All required question with hidden shown but no response
        UserResponse.objects.filter(question_id='deal_with_property_debt').update(value="Unequal division")
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.STARTED)

        # Only one required question with hidden shown and answered
        self.create_response('how_to_divide_property_debt', 'Do not divide them')
        self.assertEqual(self.check_completeness(step), True)

        # All required question with optional fields
        self.create_response('other_property_claims', 'Want these property claims')
        self.assertEqual(self.check_completeness(step), True)
        self.assertEqual(self.check_step_status(step), Status.COMPLETED)

    def test_other_orders(self):
        step = 'other_orders'

        # Step not required if other orders not wanted
        self.assertEqual(self.check_completeness(step), True)
        self.assertEqual(self.check_step_status(step), Status.HIDDEN)

        # No response should be False
        self.create_response('want_which_orders', '["Other orders"]')
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.NOT_STARTED)

        # All required question
        self.create_response('name_change_you', 'NO')
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.STARTED)

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
        self.assertEqual(self.check_step_status(step), Status.COMPLETED)

    def test_other_questions(self):
        step = 'other_questions'

        # No response should be False
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.NOT_STARTED)

        # Some required question
        self.create_response('address_to_send_official_document_street_you', '123 Cambie st')
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.STARTED)

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
        self.assertEqual(self.check_step_status(step), Status.COMPLETED)

        # Set Specific date on to empty
        UserResponse.objects.filter(question_id='divorce_take_effect_on_specific_date').update(value="")
        self.assertEqual(self.check_completeness(step), False)

    def test_filing_locations(self):
        step = 'filing_locations'

        # No response should be False
        self.assertEqual(self.check_completeness(step), False)
        self.assertEqual(self.check_step_status(step), Status.NOT_STARTED)

        # All required question
        self.create_response('court_registry_for_filing', 'Vancouver')
        self.assertEqual(self.check_completeness(step), True)
        self.assertEqual(self.check_step_status(step), Status.COMPLETED)

        # Put empty response
        UserResponse.objects.filter(question_id='court_registry_for_filing').update(value="")
        self.assertEqual(self.check_completeness(step), False)


class ChildrenStepCompletenessTestCase(TestCase):
    fixtures = ['Question.json']

    def setUp(self):
        self.user = BceidUser.objects.create(user_guid='1234')
        self.child_live_with_you = {"child_name": "Child with you", "child_birth_date": "Dec 30, 2018", "child_live_with": "Lives with you", "child_relationship_to_you": "Natural child", "child_relationship_to_spouse": "Natural child", "child_live_with_other_details": ""}
        self.child_live_with_spouse = {"child_name": "Child with spouse", "child_birth_date": "Jan 4, 2009", "child_live_with": "Lives with spouse", "child_relationship_to_you": "Adopted child", "child_relationship_to_spouse": "Adopted child", "child_live_with_other_details": ""}
        self.child_live_with_both = {"child_name": "Child with both", "child_birth_date": "Jan 4, 2009", "child_live_with": "Lives with both", "child_relationship_to_you": "Adopted child", "child_relationship_to_spouse": "Adopted child", "child_live_with_other_details": ""}
        self.create_response('children_of_marriage', 'YES')
        self.create_response('has_children_under_19', 'YES')

    def get_children_step_status(self, substep=None):
        responses_dict = get_data_for_user(self.user)
        responses_dict_by_step = get_step_responses(responses_dict)
        step_completeness = get_step_completeness(responses_dict_by_step)
        if not substep:
            key = 'your_children'
        else:
            key = f'children__{substep}'
        return step_completeness[key]

    def is_step_complete(self, substep):
        return self.get_children_step_status(substep) == Status.COMPLETED

    def create_response(self, question, value):
        response, _ = UserResponse.objects.get_or_create(bceid_user=self.user, question_id=question)
        response.value = value
        response.save()

    def delete_response(self, questions):
        if isinstance(questions, str):
            questions = [questions]
        UserResponse.objects.filter(bceid_user=self.user, question_id__in=questions).delete()

    def get_derived_value(self, derived_key):
        responses_dict = get_data_for_user(self.user)
        responses_dict_by_step = get_step_responses(responses_dict)
        responses_dict.update(get_error_dict(responses_dict_by_step))
        derived_data = get_derived_data(responses_dict)
        return derived_data[derived_key]

    def test_no_children(self):
        self.create_response('children_of_marriage', 'NO')
        self.assertEqual(self.get_children_step_status(), Status.HIDDEN)
        self.assertEqual(self.get_children_step_status('your_children'), Status.HIDDEN)
        self.assertEqual(self.get_children_step_status('income_expenses'), Status.HIDDEN)
        self.assertEqual(self.get_children_step_status('facts'), Status.HIDDEN)
        self.assertEqual(self.get_children_step_status('payor_medical'), Status.HIDDEN)
        self.assertEqual(self.get_children_step_status('what_for'), Status.HIDDEN)

    def test_only_grown_children(self):
        self.create_response('children_of_marriage', 'YES')
        self.create_response('has_children_under_19', 'NO')
        self.create_response('has_children_over_19', 'YES')
        self.create_response('children_financial_support', '["NO"]')
        self.assertEqual(self.get_children_step_status(), Status.HIDDEN)
        self.assertEqual(self.get_children_step_status('your_children'), Status.HIDDEN)
        self.assertEqual(self.get_children_step_status('income_expenses'), Status.HIDDEN)
        self.assertEqual(self.get_children_step_status('facts'), Status.HIDDEN)
        self.assertEqual(self.get_children_step_status('payor_medical'), Status.HIDDEN)
        self.assertEqual(self.get_children_step_status('what_for'), Status.HIDDEN)

    def test_has_children(self):
        self.create_response('children_of_marriage', 'YES')
        self.create_response('has_children_under_19', 'NO')
        self.create_response('has_children_over_19', 'YES')
        self.create_response('children_financial_support', '["Yes, other reason"]')
        self.assertEqual(self.get_children_step_status(), Status.NOT_STARTED)
        self.assertEqual(self.get_children_step_status('your_children'), Status.NOT_STARTED)
        self.assertEqual(self.get_children_step_status('income_expenses'), Status.NOT_STARTED)
        self.assertEqual(self.get_children_step_status('facts'), Status.NOT_STARTED)
        self.assertEqual(self.get_children_step_status('payor_medical'), Status.NOT_STARTED)
        self.assertEqual(self.get_children_step_status('what_for'), Status.NOT_STARTED)

    def test_children_details(self):
        substep = 'your_children'

        # No response status is Not Started
        self.assertFalse(self.is_step_complete(substep))
        self.assertEqual(self.get_children_step_status(substep), Status.NOT_STARTED)

        # Empty list doesn't count as answered
        self.create_response('claimant_children', '[]')
        self.assertFalse(self.is_step_complete(substep))

        # Future question answered means status is Skipped
        self.create_response('have_separation_agreement', 'YES')
        self.assertEqual(self.get_children_step_status(substep), Status.SKIPPED)

        # Has valid value
        children = [self.child_live_with_you]
        self.create_response('claimant_children', json.dumps(children))
        self.assertTrue(self.is_step_complete(substep))

    def test_income_and_expenses(self):
        substep = 'income_expenses'

        children = [self.child_live_with_you, self.child_live_with_spouse]
        self.create_response('claimant_children', json.dumps(children))
        self.assertEqual(self.get_children_step_status(substep), Status.NOT_STARTED)
        self.assertFalse(self.is_step_complete(substep))

        # All basic required fields
        self.create_response('how_will_calculate_income', 'entered agreement')
        self.assertEqual(self.get_children_step_status(substep), Status.STARTED)
        self.create_response('annual_gross_income', '100')
        self.create_response('spouse_annual_gross_income', '100')
        self.create_response('special_extraordinary_expenses', 'NO')
        self.assertTrue(self.is_step_complete(substep))

        # If there is sole custody of children, also require payor_monthly_child_support_amount
        children = [self.child_live_with_spouse]
        self.create_response('claimant_children', json.dumps(children))
        self.assertFalse(self.is_step_complete(substep))
        self.create_response('payor_monthly_child_support_amount', '100')
        self.assertTrue(self.is_step_complete(substep))

        # Fact Sheet A - at least one extraordinary expense must be input and description required
        self.create_response('special_extraordinary_expenses', 'YES')
        self.assertFalse(self.is_step_complete(substep))
        self.create_response('post_secondary_expenses', '100')
        self.assertFalse(self.is_step_complete(substep))
        self.create_response('describe_order_special_extra_expenses', 'Some expenses')
        self.assertTrue(self.is_step_complete(substep))

    def test_payor_and_fact_sheets(self):
        substep = 'facts'

        children = [self.child_live_with_you]
        self.create_response('claimant_children', json.dumps(children))
        self.create_response('annual_gross_income', '0')
        self.assertEqual(self.get_children_step_status(substep), Status.NOT_STARTED)
        self.assertFalse(self.is_step_complete(substep))

        # All basic required fields if there is only sole custody of children and payor makes less than $150,000
        self.create_response('child_support_payor', 'Myself (Claimant 1)')
        self.create_response('claiming_undue_hardship', 'NO')
        self.assertTrue(self.is_step_complete(substep))

    def test_fact_sheet_b(self):
        # Don't show fact sheet
        self.assertFalse(self.get_derived_value('show_fact_sheet_b'))
        self.assertFalse(self.get_derived_value('fact_sheet_b_error'))

        # Must have shared custody to show fact sheet
        children = [self.child_live_with_both]
        self.create_response('claimant_children', json.dumps(children))
        self.assertTrue(self.get_derived_value('show_fact_sheet_b'))
        self.assertTrue(self.get_derived_value('fact_sheet_b_error'))

        # Basic required fields
        self.create_response('time_spent_with_you', '50')
        self.create_response('time_spent_with_spouse', '50')
        self.create_response('your_child_support_paid_b', '100')
        self.create_response('your_spouse_child_support_paid_b', '1000')
        self.assertFalse(self.get_derived_value('fact_sheet_b_error'))

    def test_fact_sheet_c(self):
        # Don't show fact sheet
        self.assertFalse(self.get_derived_value('show_fact_sheet_c'))
        self.assertFalse(self.get_derived_value('fact_sheet_c_error'))

        # Must have split custody to show fact sheet
        children = [self.child_live_with_both, self.child_live_with_you]
        self.create_response('claimant_children', json.dumps(children))
        self.assertTrue(self.get_derived_value('show_fact_sheet_c'))
        self.assertTrue(self.get_derived_value('fact_sheet_c_error'))

        # Basic required fields
        self.create_response('your_spouse_child_support_paid_c', '50')
        self.create_response('your_child_support_paid_c', '0')
        self.assertFalse(self.get_derived_value('fact_sheet_c_error'))

    def test_fact_sheet_d(self):
        # Don't show fact sheet
        self.create_response('children_of_marriage', 'YES')
        self.create_response('has_children_over_19', 'NO')
        self.assertFalse(self.get_derived_value('show_fact_sheet_d'))
        self.assertFalse(self.get_derived_value('fact_sheet_d_error'))

        # Must be supporting children over 19 to show fact sheet
        self.create_response('has_children_over_19', 'YES')
        self.create_response('children_financial_support', '["NO"]')
        self.assertFalse(self.get_derived_value('show_fact_sheet_d'))

        self.create_response('children_financial_support', '["Yes, other reason"]')
        self.assertTrue(self.get_derived_value('show_fact_sheet_d'))
        self.assertTrue(self.get_derived_value('fact_sheet_d_error'))

        # Basic required fields
        self.create_response('number_children_over_19_need_support', '1')
        self.create_response('agree_to_guideline_child_support_amount', 'YES')
        self.assertFalse(self.get_derived_value('fact_sheet_d_error'))

        # Conditional fields
        self.create_response('agree_to_guideline_child_support_amount', 'NO')
        self.create_response('appropriate_spouse_paid_child_support', '1000')
        self.create_response('suggested_child_support', 'Because')
        self.assertFalse(self.get_derived_value('fact_sheet_d_error'))

    def test_fact_sheet_e(self):
        # Don't show fact sheet
        self.create_response('claiming_undue_hardship', 'NO')
        self.assertFalse(self.get_derived_value('show_fact_sheet_e'))
        self.assertFalse(self.get_derived_value('fact_sheet_e_error'))

        # Make at least one undue hardship required
        self.create_response('claiming_undue_hardship', 'YES')
        self.assertTrue(self.get_derived_value('show_fact_sheet_e'))
        self.assertTrue(self.get_derived_value('fact_sheet_e_error'))

        self.create_response('claimant_expenses', '[{"expense_name":"Daycare","expense_amount":"2000"}]')
        self.assertFalse(self.get_derived_value('fact_sheet_e_error'))

        self.delete_response('claimant_expenses')
        self.create_response('undue_hardship', 'Some hardships')
        self.assertFalse(self.get_derived_value('fact_sheet_e_error'))

    def test_fact_sheet_f_you(self):
        # Don't show fact sheet
        self.create_response('child_support_payor', 'Both myself and my spouse')
        self.create_response('annual_gross_income', '150000')
        self.assertFalse(self.get_derived_value('show_fact_sheet_f'))
        self.assertFalse(self.get_derived_value('fact_sheet_f_error'))

        # Show fact sheet for claimant 1
        self.create_response('annual_gross_income', '150001')
        self.assertTrue(self.get_derived_value('show_fact_sheet_f'))
        self.assertTrue(self.get_derived_value('fact_sheet_f_error'))

        # Basic required fields
        self.create_response('number_children_seeking_support_you', '1')
        self.create_response('child_support_amount_under_high_income_you', '1000')
        self.create_response('percent_income_over_high_income_limit_you', '10')
        self.create_response('amount_income_over_high_income_limit_you', '1')
        self.create_response('agree_to_child_support_amount_you', 'YES')
        self.assertFalse(self.get_derived_value('fact_sheet_f_error'))

        # Conditional fields
        self.create_response('agree_to_child_support_amount_you', 'NO')
        self.assertTrue(self.get_derived_value('fact_sheet_f_error'))
        self.create_response('agreed_child_support_amount_you', '1000')
        self.create_response('reason_child_support_amount_you', 'Because')
        self.assertFalse(self.get_derived_value('fact_sheet_f_error'))

    def test_fact_sheet_f_spouse(self):
        # Don't show fact sheet
        self.create_response('child_support_payor', 'Both myself and my spouse')
        self.create_response('spouse_annual_gross_income', '150000')
        self.assertFalse(self.get_derived_value('show_fact_sheet_f'))
        self.assertFalse(self.get_derived_value('fact_sheet_f_error'))

        # Show fact sheet for claimant 2
        self.create_response('spouse_annual_gross_income', '150001')
        self.assertTrue(self.get_derived_value('show_fact_sheet_f'))
        self.assertTrue(self.get_derived_value('fact_sheet_f_error'))

        # Basic required fields
        self.create_response('number_children_seeking_support_spouse', '1')
        self.create_response('child_support_amount_under_high_income_spouse', '1000')
        self.create_response('percent_income_over_high_income_limit_spouse', '10')
        self.create_response('amount_income_over_high_income_limit_spouse', '1')
        self.create_response('agree_to_child_support_amount_spouse', 'YES')
        self.assertFalse(self.get_derived_value('fact_sheet_f_error'))

        # Conditional fields
        self.create_response('agree_to_child_support_amount_spouse', 'NO')
        self.assertTrue(self.get_derived_value('fact_sheet_f_error'))
        self.create_response('agreed_child_support_amount_spouse', '1000')
        self.create_response('reason_child_support_amount_spouse', 'Because')
        self.assertFalse(self.get_derived_value('fact_sheet_f_error'))

    def test_payor_medical(self):
        substep = 'payor_medical'

        self.assertFalse(self.is_step_complete(substep))
        self.assertEqual(self.get_children_step_status(substep), Status.NOT_STARTED)

        # All basic required fields
        self.create_response('medical_coverage_available', 'NO')
        self.create_response('child_support_payments_in_arrears', 'NO')
        self.assertTrue(self.is_step_complete(substep))

        # Conditionally required fields
        self.create_response('medical_coverage_available', 'YES')
        self.assertFalse(self.is_step_complete(substep))
        self.create_response('whose_plan_is_coverage_under', '[]')

        self.assertFalse(self.is_step_complete(substep))
        self.create_response('whose_plan_is_coverage_under', '["My plan","Spouse"]')
        self.assertTrue(self.is_step_complete(substep))

    def test_what_are_you_asking_for(self):
        substep = 'what_for'

        self.assertFalse(self.is_step_complete(substep))
        self.assertEqual(self.get_children_step_status(substep), Status.NOT_STARTED)

        # All basic required fields
        self.create_response('child_support_in_order', 'MATCH')
        self.create_response('have_separation_agreement', 'NO')
        self.create_response('have_court_order', 'NO')
        self.create_response('what_parenting_arrangements', 'Something')
        self.create_response('want_parenting_arrangements', 'NO')
        self.create_response('child_support_act', 'NO')
        self.assertFalse(self.is_step_complete(substep))

        # Based on child_support_in_order value (MATCH)
        self.create_response('order_for_child_support', 'We are asking for X')
        self.assertTrue(self.is_step_complete(substep))

        # Based on child_support_in_order value (DIFF)
        self.create_response('child_support_in_order', 'DIFF')
        self.assertFalse(self.is_step_complete(substep))
        self.create_response('order_monthly_child_support_amount', '100')
        self.create_response('claimants_agree_to_child_support_amount', 'YES')
        self.assertTrue(self.is_step_complete(substep))
        self.create_response('claimants_agree_to_child_support_amount', 'NO')
        self.create_response('child_support_payment_special_provisions', 'Some special provisions')
        self.assertTrue(self.is_step_complete(substep))

        # Based on child_support_in_order value (NO)
        self.create_response('child_support_in_order', 'NO')
        self.assertFalse(self.is_step_complete(substep))
        self.create_response('child_support_in_order_reason', 'We will sort it out ourselves')
        self.delete_response(['order_for_child_support', 'claimants_agree_to_child_support_amount', 'child_support_payment_special_provisions'])
        self.assertTrue(self.is_step_complete(substep))

        # Other conditionals
        self.create_response('want_parenting_arrangements', 'YES')
        self.assertFalse(self.is_step_complete(substep))
        self.create_response('order_respecting_arrangement', 'Claimant 1 and Claimant 2 will share parenting time equally between them.')
        self.assertTrue(self.is_step_complete(substep))
