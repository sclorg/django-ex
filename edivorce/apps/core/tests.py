from django.test import TestCase
from edivorce.apps.core.models import UserResponse, Question, BceidUser
from edivorce.apps.core.utils.step_completeness import is_complete
from edivorce.apps.core.utils.question_step_mapping import question_step_mapping


# Create your tests here.
class UserResponseTestCase(TestCase):
    fixtures = ['Question.json']

    def setUp(self):
        BceidUser.objects.create(user_guid='1234')

    def test_which_order(self):
        step = 'which_orders'
        questions = question_step_mapping[step]
        user = BceidUser.objects.get(user_guid='1234')

        # No response should be False
        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required question
        create_response(user, 'want_which_orders', '["nothing"]')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # Put empty response
        UserResponse.objects.filter(question_id='want_which_orders').update(value="[]")

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

    def test_your_info(self):
        step = 'your_information'
        questions = question_step_mapping[step]
        user = BceidUser.objects.get(user_guid='1234')

        # No response should be False
        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Testing required questions
        # Missing few required questions
        create_response(user, 'name_you', 'John Doe')
        create_response(user, 'last_name_before_married_you', 'Jackson')
        create_response(user, 'birthday_you', '11/11/1111')
        create_response(user, 'occupation_you', 'Plumber')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Few required questions with one checking question with hidden question not shown
        create_response(user, 'lived_in_bc_you', '11/11/1111')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required questions with one checking question with hidden question not shown
        create_response(user, 'last_name_born_you', 'Jackson')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required questions with one checking question with hidden question missing
        UserResponse.objects.filter(question_id='lived_in_bc_you').update(value="Moved to B.C. on")

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required questions with one checking question with hidden question
        create_response(user, 'moved_to_bc_date_you', '12/12/1212')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required questions with two checking question with one hidden and one shown
        create_response(user, 'any_other_name_you', 'NO')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # All required questions with two checking question with one hidden question missing
        UserResponse.objects.filter(question_id='any_other_name_you').update(value="YES")

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required questions with all checking question with all hidden questions
        create_response(user, 'other_name_you', '[["also known as","Smith"]]')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # Put empty response
        UserResponse.objects.filter(question_id='other_name_you').update(value='[["",""]]')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

    def test_your_spouse(self):
        step = 'your_spouse'
        questions = question_step_mapping[step]
        user = BceidUser.objects.get(user_guid='1234')

        # No response should be False
        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Testing required questions
        # Missing few required questions
        create_response(user, 'name_spouse', 'John Doe')
        create_response(user, 'last_name_before_married_spouse', 'Jackson')
        create_response(user, 'birthday_spouse', '11/11/1111')
        create_response(user, 'occupation_spouse', 'Electrician')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Few required questions with one checking question with hidden question not shown
        create_response(user, 'any_other_name_spouse', 'NO')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required questions with one checking question with hidden question not shown
        create_response(user, 'last_name_born_spouse', 'Jackson')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required questions with one checking question with hidden question missing
        UserResponse.objects.filter(question_id='any_other_name_spouse').update(value="YES")

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required questions with one checking question with hidden question
        create_response(user, 'lived_in_bc_spouse', 'Since birth')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required questions with two checking question with one hidden and one shown
        create_response(user, 'other_name_spouse', '[["also known as","Smith"]]')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # All required questions with two checking question with one hidden question missing
        UserResponse.objects.filter(question_id='lived_in_bc_spouse').update(value="Moved to B.C. on")

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required questions with all checking question with all hidden questions
        create_response(user, 'moved_to_bc_date_spouse', '12/12/1212')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # Put empty response
        UserResponse.objects.filter(question_id='name_spouse').update(value="")

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Put empty response
        UserResponse.objects.filter(question_id='other_name_spouse').update(value='[["",""]]')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

    def test_your_marriage(self):
        step = 'your_marriage'
        questions = question_step_mapping[step]
        user = BceidUser.objects.get(user_guid='1234')

        # No response should be False
        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Test for marriage-like relationship
        create_response(user, 'married_marriage_like', 'Living together in a marriage like relationship')
        questions.append('married_marriage_like')

        # One required question
        create_response(user, 'when_were_you_live_married_like', '12/12/2007')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # One required question and one not shown question(shouldn't be affecting)
        create_response(user, 'when_were_you_married', '12/12/2008')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Two required question and one not shown question(shouldn't be affecting)
        create_response(user, 'marital_status_before_you', 'Never married')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required question and one not shown question(shouldn't be affecting)
        create_response(user, 'marital_status_before_spouse', 'Widowed')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # Test for Legally Married state
        UserResponse.objects.filter(question_id='married_marriage_like').update(value="Legally married")

        # Missing some required questions
        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Some required questions
        create_response(user, 'where_were_you_married_city', 'Vancouver')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Some required questions
        create_response(user, 'where_were_you_married_prov', 'BC')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required questions
        create_response(user, 'where_were_you_married_country', 'Canada')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # All required questions but missing conditional question
        UserResponse.objects.filter(question_id='where_were_you_married_country').update(value="Other")

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required questions
        create_response(user, 'where_were_you_married_other_country', 'Peru')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

    def test_your_separation(self):
        step = 'your_separation'
        questions = question_step_mapping[step]
        user = BceidUser.objects.get(user_guid='1234')

        # No response should be False
        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required question
        create_response(user, 'no_reconciliation_possible', 'I agree')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Put empty response
        UserResponse.objects.filter(question_id='no_reconciliation_possible').update(value="")

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

    def test_spousal_support(self):
        step = 'spousal_support'
        questions = question_step_mapping[step]
        user = BceidUser.objects.get(user_guid='1234')

        # No response should be False
        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # One required question
        create_response(user, 'spouse_support_details', 'I will support you')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Two required questions
        create_response(user, 'spouse_support_act', 'Family Law')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # Remove first added required response to test the second required question
        UserResponse.objects.get(question_id='spouse_support_details').delete()

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Put empty response
        UserResponse.objects.filter(question_id='spouse_support_details').update(value="")

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

    def test_property_and_debt(self):
        step = 'property_and_debt'
        questions = question_step_mapping[step]
        user = BceidUser.objects.get(user_guid='1234')

        # No response should be False
        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required question with no hidden shown
        create_response(user, 'deal_with_property_debt', 'Equal division')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # All required question with hidden shown but no response
        UserResponse.objects.filter(question_id='deal_with_property_debt').update(value="Unequal division")

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Only one required question with hidden shown and answered
        create_response(user, 'how_to_divide_property_debt', 'Do not divide them')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # Only two required question with hidden shown and answered
        # NOTE: want_other_property_claims not in use anymore
        # create_response(user, 'want_other_property_claims', '["Ask for other property claims"]')
        #
        # lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        # self.assertEqual(is_complete(step, lst)[0], False)

        # All required question with hidden shown and answered
        create_response(user, 'other_property_claims', 'Want these property claims')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # Put empty response
        # UserResponse.objects.filter(question_id='want_other_property_claims').update(value="")

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

    def test_other_orders(self):
        step = 'other_orders'
        questions = question_step_mapping[step]
        user = BceidUser.objects.get(user_guid='1234')

        # No response should be False
        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required question

        create_response(user, 'name_change_you', 'NO')
        self.assertEqual(is_complete(step, lst)[0], False)

        create_response(user, 'name_change_spouse', 'NO')
        create_response(user, 'other_orders_detail', 'I want more orders')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # make incomplete
        UserResponse.objects.filter(question_id='name_change_spouse').update(value="YES")

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        create_response(user, 'name_change_spouse_fullname', 'new name')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # Put empty response
        UserResponse.objects.filter(question_id='other_orders_detail').update(value="")

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

    def test_other_questions(self):
        step = 'other_questions'
        questions = question_step_mapping[step]
        user = BceidUser.objects.get(user_guid='1234')

        # No response should be False
        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Test for marriage-like relationship
        create_response(user, 'married_marriage_like', 'Living together in a marriage like relationship')
        questions.append('married_marriage_like')

        # One required question
        create_response(user, 'address_to_send_official_document_street_you', '123 Cambie st')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Two required question
        create_response(user, 'address_to_send_official_document_city_you', 'Vancouver')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Three required question
        create_response(user, 'address_to_send_official_document_prov_you', 'BC')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Four required question
        create_response(user, 'address_to_send_official_document_country_you', 'Canada')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required questions for you
        create_response(user, 'address_to_send_official_document_postal_code_you', 'Canada')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # One required question for spouse
        create_response(user, 'address_to_send_official_document_street_spouse', '123 Cambie st')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Two required question for spouse
        create_response(user, 'address_to_send_official_document_city_spouse', 'Vancouver')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Three required question for spouse
        create_response(user, 'address_to_send_official_document_prov_spouse', 'BC')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # Four required question for spouse
        create_response(user, 'address_to_send_official_document_country_spouse', 'Canada')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required questions for spouse and you
        create_response(user, 'address_to_send_official_document_postal_code_spouse', 'Canada')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # All required questions for spouse and you with empty email(optional so still true)
        create_response(user, 'address_to_send_official_document_email_you', 'a@example.com')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # Test for Legally Married state
        UserResponse.objects.filter(question_id='married_marriage_like').update(value="Legally married")

        # Missing some required questions for legally married state
        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required questions
        create_response(user, 'divorce_take_effect_on', 'the 31st day after the date of this order')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # Missing required question
        UserResponse.objects.filter(question_id='divorce_take_effect_on').update(value="specific date")

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required questions
        create_response(user, 'divorce_take_effect_on_specific_date', '12/12/2018')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # Testing other country missing
        UserResponse.objects.filter(question_id='address_to_send_official_document_country_spouse').update(value="Other")

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required questions
        create_response(user, 'address_to_send_official_document_other_country_spouse', 'Mexico')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # Set Specific date on to empty
        UserResponse.objects.filter(question_id='divorce_take_effect_on_specific_date').update(value="")

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value',
                                                                            'question__conditional_target',
                                                                            'question__reveal_response',
                                                                            'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

    def test_filing_locations(self):
        step = 'filing_locations'
        questions = question_step_mapping[step]
        user = BceidUser.objects.get(user_guid='1234')

        # No response should be False
        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)

        # All required question
        create_response(user, 'court_registry_for_filing', 'Vancouver')

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], True)

        # Put empty response
        UserResponse.objects.filter(question_id='court_registry_for_filing').update(value="")

        lst = UserResponse.objects.filter(question_id__in=questions).values('question_id', 'value', 'question__conditional_target', 'question__reveal_response', 'question__required')
        self.assertEqual(is_complete(step, lst)[0], False)


# Helper functions
def create_response(user, question, value):
    UserResponse.objects.create(bceid_user=user, question=Question.objects.get(key=question), value=value)
