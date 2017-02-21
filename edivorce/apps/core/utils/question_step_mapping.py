"""
    Mapping between questions and steps
    Usage: For each step title, list all questions_keys belong to that step
"""
question_step_mapping = {'prequalification': ['married_marriage_like', 'lived_in_bc', 'lived_in_bc_at_least_year', 'separation_date',
                                              'children_of_marriage', 'any_under_19', 'children_financial_support', 'original_marriage_certificate',
                                              'provide_certificate_later', 'provide_certificate_later_reason', 'not_provide_certificate_reason',
                                              'divorce_reason', 'marriage_certificate_in_english', 'try_reconcile_after_separated'],
                         'which_orders': ['want_which_orders',],
                         'your_information': ['name_you', 'any_other_name_you', 'other_name_you', 'last_name_born_you',
                                              'last_name_before_married_you', 'birthday_you', 'lived_in_bc_you', 'moved_to_bc_date_you',],
                         'your_spouse': ['name_spouse', 'any_other_name_spouse', 'other_name_spouse', 'last_name_born_spouse',
                                         'last_name_before_married_spouse', 'birthday_spouse', 'lived_in_bc_spouse', 'moved_to_bc_date_spouse',],
                         'your_marriage': ['when_were_you_married', 'where_were_you_married_city', 'where_were_you_married_prov',
                                           'where_were_you_married_country', 'where_were_you_married_other_country', 'marital_status_before_you',
                                           'marital_status_before_spouse',],
                         'your_separation': ['no_reconciliation_possible', 'no_collusion',],
                         'spousal_support': ['spouse_support_details', 'spouse_support_act',],
                         'property_and_debt': ['deal_with_property_debt', 'how_to_divide_property_debt', 'other_property_claims',],
                         'other_orders': [],
                         'other_questions': [],
                         'filing_locations': ['address_to_send_official_document_street', 'address_to_send_official_document_city',
                                              'address_to_send_official_document_prov', 'address_to_send_official_document_country',
                                              'address_to_send_official_document_other_country', 'address_to_send_official_document_fax',
                                              'address_to_send_official_document_email', 'court_registry_for_filing',],
                         }
