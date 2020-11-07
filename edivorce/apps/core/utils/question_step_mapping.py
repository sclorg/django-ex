"""
    Mapping between steps in the pre-qualification stage and the questions on each
    step. Useful for showing a human readable link and message when a question is not
    answered. The user can click the link to take them back to the step containing the
    unanswered question.
"""
pre_qual_step_question_mapping = {
    '01': {
        'married_marriage_like'
    },
    '02': {
        'lived_in_bc',
        'lived_in_bc_at_least_year'
    },
    '03': {
        'separation_date',
        'try_reconcile_after_separated',
        'reconciliation_period'
    },
    '04': {
        'children_of_marriage',
        'has_children_under_19',
        'has_children_over_19',
        'children_financial_support',
        'children_live_with_others'
    },
    '05': {
        'original_marriage_certificate',
        'provide_certificate_later',
        'provide_certificate_later_reason',
        'not_provide_certificate_reason',
        'marriage_certificate_in_english'
    },
    '06': {
        'divorce_reason',
    }
}

children_substep_question_mapping = {
    'your_children': {
        'claimant_children'
    },
    'income_expenses': {
        'how_will_calculate_income',
        'annual_gross_income',
        'spouse_annual_gross_income',
        'payor_monthly_child_support_amount',
        'special_extraordinary_expenses',
        'child_care_expenses',
        'children_healthcare_premiums',
        'health_related_expenses',
        'extraordinary_educational_expenses',
        'post_secondary_expenses',
        'extraordinary_extracurricular_expenses',
        'total_section_seven_expenses',
        'your_proportionate_share_percent',
        'your_proportionate_share_amount',
        'spouse_proportionate_share_percent',
        'spouse_proportionate_share_amount',
        'describe_order_special_extra_expenses',
    },
    'facts': {
        'child_support_payor',
        # Fact sheet B
        'time_spent_with_you',
        'time_spent_with_spouse',
        'your_child_support_paid_b',
        'your_spouse_child_support_paid_b',
        'additional_relevant_spouse_children_info',
        # Fact sheet C
        'your_spouse_child_support_paid_c',
        'your_child_support_paid_c',
        # Fact sheet D
        'number_children_over_19_need_support',
        'agree_to_guideline_child_support_amount',
        'appropriate_spouse_paid_child_support',
        'suggested_child_support',
        # Fact sheet E
        'claiming_undue_hardship',
        'claimant_debts',
        'claimant_expenses',
        'supporting_non_dependents',
        'supporting_dependents',
        'supporting_disabled',
        'undue_hardship',
        'income_others',
        # Fact sheet F
        'number_children_seeking_support_you',
        'child_support_amount_under_high_income_you',
        'percent_income_over_high_income_limit_you',
        'amount_income_over_high_income_limit_you',
        'total_guideline_amount_you',
        'agree_to_child_support_amount_you',
        'agreed_child_support_amount_you',
        'reason_child_support_amount_you',
        'number_children_seeking_support_spouse',
        'child_support_amount_under_high_income_spouse',
        'percent_income_over_high_income_limit_spouse',
        'amount_income_over_high_income_limit_spouse',
        'total_guideline_amount_spouse',
        'agree_to_child_support_amount_spouse',
        'agreed_child_support_amount_spouse',
        'reason_child_support_amount_spouse',
    },
    'payor_medical': {
        'medical_coverage_available',
        'whose_plan_is_coverage_under',
        'child_support_payments_in_arrears',
        'child_support_arrears_amount',
    },
    'what_for': {
        # child_support_in_order is not here because it can get pre-populated, and we don't want
        # it to be counted as an "answer" for determining Skipped and Started statuses
        'order_monthly_child_support_amount',
        'child_support_in_order_reason',
        'claimants_agree_to_child_support_amount',
        'child_support_payment_special_provisions',
        'have_separation_agreement',
        'have_court_order',
        'what_parenting_arrangements',
        'want_parenting_arrangements',
        'order_respecting_arrangement',
        'order_for_child_support',
        'child_support_act'
    },
}

"""
    Mapping between questions and steps
    Usage: For each step title, list all questions_keys belong to that step
"""
question_step_mapping = {
    'prequalification': ['married_marriage_like',
                         'lived_in_bc',
                         'lived_in_bc_at_least_year',
                         'separation_date',
                         'try_reconcile_after_separated',
                         'reconciliation_period',
                         'children_of_marriage',
                         'has_children_under_19',
                         'has_children_over_19',
                         'children_financial_support',
                         'children_live_with_others',
                         'original_marriage_certificate',
                         'provide_certificate_later',
                         'provide_certificate_later_reason',
                         'not_provide_certificate_reason',
                         'marriage_certificate_in_english',
                         'divorce_reason'],
    'which_orders': ['want_which_orders'],
    'your_information': ['last_name_you',
                         'given_name_1_you',
                         'given_name_2_you',
                         'given_name_3_you',
                         'any_other_name_you',
                         'other_name_you',
                         'last_name_born_you',
                         'last_name_before_married_you',
                         'birthday_you',
                         'occupation_you',
                         'lived_in_bc_you',
                         'moved_to_bc_date_you',],
    'your_spouse': ['last_name_spouse',
                    'given_name_1_spouse',
                    'given_name_2_spouse',
                    'given_name_3_spouse',
                    'any_other_name_spouse',
                    'other_name_spouse',
                    'last_name_born_spouse',
                    'last_name_before_married_spouse',
                    'birthday_spouse',
                    'occupation_spouse',
                    'lived_in_bc_spouse',
                    'moved_to_bc_date_spouse',],
    'your_marriage': ['when_were_you_married',
                      'where_were_you_married_city',
                      'where_were_you_married_prov',
                      'where_were_you_married_country',
                      'where_were_you_married_other_country',
                      'marital_status_before_you',
                      'marital_status_before_spouse',
                      'when_were_you_live_married_like'],
    'your_separation': ['no_reconciliation_possible',
                        'no_collusion'],
    'your_children': ['claimant_children',
                      # Income & Expenses
                      'how_will_calculate_income',
                      'annual_gross_income',
                      'spouse_annual_gross_income',
                      'payor_monthly_child_support_amount',
                      # Fact sheet A
                      'special_extraordinary_expenses',
                      'child_care_expenses',
                      'children_healthcare_premiums',
                      'health_related_expenses',
                      'extraordinary_educational_expenses',
                      'post_secondary_expenses',
                      'extraordinary_extracurricular_expenses',
                      'describe_order_special_extra_expenses',
                      # Payor & Fact Sheets
                      'child_support_payor',
                      # Fact sheet B
                      'time_spent_with_you',
                      'time_spent_with_spouse',
                      'your_child_support_paid_b',
                      'your_spouse_child_support_paid_b',
                      'additional_relevant_spouse_children_info',
                      # Fact sheet C
                      'your_spouse_child_support_paid_c',
                      'your_child_support_paid_c',
                      # Fact sheet D
                      'number_children_over_19_need_support',
                      'agree_to_guideline_child_support_amount',
                      'appropriate_spouse_paid_child_support',
                      'suggested_child_support',
                      # Fact sheet E
                      'claiming_undue_hardship',
                      'claimant_debts',
                      'claimant_expenses',
                      'supporting_non_dependents',
                      'supporting_dependents',
                      'supporting_disabled',
                      'undue_hardship',
                      'income_others',
                      # Fact sheet F
                      'number_children_seeking_support_you',
                      'child_support_amount_under_high_income_you',
                      'percent_income_over_high_income_limit_you',
                      'amount_income_over_high_income_limit_you',
                      'total_guideline_amount_you',
                      'agree_to_child_support_amount_you',
                      'agreed_child_support_amount_you',
                      'reason_child_support_amount_you',
                      'number_children_seeking_support_spouse',
                      'child_support_amount_under_high_income_spouse',
                      'percent_income_over_high_income_limit_spouse',
                      'amount_income_over_high_income_limit_spouse',
                      'total_guideline_amount_spouse',
                      'agree_to_child_support_amount_spouse',
                      'agreed_child_support_amount_spouse',
                      'reason_child_support_amount_spouse',
                      # Medical and other expenses
                      'medical_coverage_available',
                      'whose_plan_is_coverage_under',
                      'child_support_payments_in_arrears',
                      'child_support_arrears_amount',
                      # What are you asking for
                      'child_support_in_order',
                      'order_monthly_child_support_amount',
                      'child_support_in_order_reason',
                      'claimants_agree_to_child_support_amount',
                      'child_support_payment_special_provisions',
                      'have_separation_agreement',
                      'have_court_order',
                      'what_parenting_arrangements',
                      'want_parenting_arrangements',
                      'order_respecting_arrangement',
                      'order_for_child_support',
                      'child_support_act'],
    'spousal_support': ['spouse_support_details',
                        'spouse_support_act'],
    'property_and_debt': ['deal_with_property_debt',
                          'how_to_divide_property_debt',
                          'other_property_claims'],
    'other_orders': ['name_change_you',
                     'name_change_you_fullname',
                     'name_change_spouse',
                     'name_change_spouse_fullname',
                     'other_orders_detail'],
    'other_questions': ['address_to_send_official_document_street_you',
                        'address_to_send_official_document_city_you',
                        'address_to_send_official_document_prov_you',
                        'address_to_send_official_document_country_you',
                        'address_to_send_official_document_other_country_you',
                        'address_to_send_official_document_postal_code_you',
                        'address_to_send_official_document_fax_you',
                        'address_to_send_official_document_email_you',
                        'address_to_send_official_document_street_spouse',
                        'address_to_send_official_document_city_spouse',
                        'address_to_send_official_document_prov_spouse',
                        'address_to_send_official_document_country_spouse',
                        'address_to_send_official_document_other_country_spouse',
                        'address_to_send_official_document_postal_code_spouse',
                        'address_to_send_official_document_fax_spouse',
                        'address_to_send_official_document_email_spouse',
                        'divorce_take_effect_on',
                        'divorce_take_effect_on_specific_date'],
    'filing_locations': ['court_registry_for_filing'],
    'signing_filing': ['how_to_sign',
                       'how_to_file',
                       'signing_location',
                       'signing_location_you',
                       'signing_location_spouse',
                       'email_you',
                       'email_spouse'],
}

page_step_mapping = {
    'prequalification': 'prequalification',
    'orders': 'which_orders',
    'claimant': 'your_information',
    'respondent': 'your_spouse',
    'marriage': 'your_marriage',
    'separation': 'your_separation',
    'children': 'your_children',
    'support': 'spousal_support',
    'property': 'property_and_debt',
    'other_orders': 'other_orders',
    'other_questions': 'other_questions',
    'location': 'filing_locations',
    'signing_filing': 'signing_filing',
}

""" List of court registries """
list_of_registries = {
    'Abbotsford': {
        'address_1': '32203 South Fraser Way',
        'address_2': '',
        'postal': 'V2T 1W6',
        'location_id': '3561'
    },    
    'Campbell River': {
        'address_1': '500 - 13th Avenue',
        'address_2': '',
        'postal': 'V9W 6P1',
        'location_id': '1031'
    },
    'Chilliwack': {
        'address_1': '46085 Yale Road',
        'address_2': '',
        'postal': 'V2P 2L8',
        'location_id': '3521'
    },
    'Courtenay': {
        'address_1': 'Room 100',
        'address_2': '420 Cumberland Road',
        'postal': 'V9N 2C4',
        'location_id': '1041'
    },
    'Cranbrook': {
        'address_1': 'Room 147',
        'address_2': '102 - 11th Avenue South',
        'postal': 'V1C 2P3',
        'location_id': '4711'
    },
    'Dawson Creek': {
        'address_1': '1201 - 103rd Avenue',
        'address_2': '',
        'postal': 'V1G 4J2',
        'location_id': '5731'
    },
    'Duncan': {
        'address_1': '238 Government Street',
        'address_2': '',
        'postal': 'V9L 1A5',
        'location_id': '1051'
    },
    'Fort Nelson': {
        'address_1': 'Bag 1000',
        'address_2': '4604 Sunset Drive',
        'postal': 'V0C 1R0',
        'location_id': '5751'
    },
    'Fort St. John': {
        'address_1': '10600 - 100 Street',
        'address_2': '',
        'postal': 'V1J 4L6',
        'location_id': '5771'
    },
    'Golden': {
        'address_1': '837 Park Drive',
        'address_2': '',
        'postal': 'V0A 1H0',
        'location_id': '4741'
    },
    'Kamloops': {
        'address_1': '223 - 455 Columbia Street',
        'address_2': '',
        'postal': 'V2C 6K4',
        'location_id': '4781'
    },
    'Kelowna': {
        'address_1': '1355 Water Street',
        'address_2': '',
        'postal': 'V1Y 9R3',
        'location_id': '4801'
    },
    'Nanaimo': {
        'address_1': '35 Front Street',
        'address_2': '',
        'postal': 'V9R 5J1',
        'location_id': '1091'
    },
    'Nelson': {
        'address_1': '320 Ward Street',
        'address_2': '',
        'postal': 'V1L 1S6',
        'location_id': '4871'
    },
    'New Westminster': {
        'address_1': 'Begbie Square',
        'address_2': '651 Carnarvon Street',
        'postal': 'V3M 1C9',
        'location_id': '3581'
    },
    'Penticton': {
        'address_1': '100 Main Street',
        'address_2': '',
        'postal': 'V2A 5A5',
        'location_id': '4891'
    },
    'Port Alberni': {
        'address_1': '2999 - 4th Avenue',
        'address_2': '',
        'postal': 'V9Y 8A5',
        'location_id': '1121'
    },
    'Powell River': {
        'address_1': '103 - 6953 Alberni Street',
        'address_2': '',
        'postal': 'V8A 2B8',
        'location_id': '1145'
    },
    'Prince George': {
        'address_1': 'J.O. Wilson Square',
        'address_2': '250 George Street',
        'postal': 'V2L 5S2',
        'location_id': '5891'
    },
    'Prince Rupert': {
        'address_1': '100 Market Place',
        'address_2': '',
        'postal': 'V8J 1B8',
        'location_id': '5901'
    },
    'Quesnel': {
        'address_1': '305 - 350 Barlow Avenue',
        'address_2': '',
        'postal': 'V2J 2C1',
        'location_id': '5921'
    },
    'Revelstoke': {
        'address_1': '1123 West 2nd Street',
        'address_2': '',
        'postal': 'V0E 2S0',
        'location_id': '4911'
    },
    'Rossland': {
        'address_1': 'P.O. Box 639',
        'address_2': '2288 Columbia Avenue',
        'postal': 'V0G 1Y0',
        'location_id': '4921'
    },
    'Salmon Arm': {
        'address_1': '550 - 2nd Avenue NE',
        'address_2': 'PO Box 100, Station Main',
        'postal': 'V1E 4S4',
        'location_id': '4941'
    },
    'Smithers': {
        'address_1': 'No. 40, Bag 5000',
        'address_2': '3793 Alfred Avenue',
        'postal': 'V0J 2N0',
        'location_id': '5931'
    },
    'Terrace': {
        'address_1': '3408 Kalum Street',
        'address_2': '',
        'postal': 'V8G 2N6',
        'location_id': '5951'
    },
    'Vancouver': {
        'address_1': '800 Smithe Street',
        'address_2': '',
        'postal': 'V6Z 2E1',
        'location_id': '6011'
    },
    'Vernon': {
        'address_1': '3001 - 27th Street',
        'address_2': '',
        'postal': 'V1T 4W5',
        'location_id': '4971'
    },
    'Victoria': {
        'address_1': '850 Burdett Avenue',
        'address_2': '',
        'postal': 'V8W 1B4',
        'location_id': '1201'
    },
    'Williams Lake': {
        'address_1': '540 Borland Street',
        'address_2': '',
        'postal': 'V2G lR8',
        'location_id': '5971'
    }
}
