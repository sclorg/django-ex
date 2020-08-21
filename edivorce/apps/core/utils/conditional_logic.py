import json


def get_children(questions_dict):
    children_json = questions_dict.get('claimant_children', '[]')
    if isinstance(children_json, dict):
        children_json = children_json.get('value', '[]')
    return json.loads(children_json)


def determine_sole_custody(questions_dict):
    child_list = get_children(questions_dict)
    return (all([child['child_live_with'] == 'Lives with you' for child in child_list]) or
            all([child['child_live_with'] == 'Lives with spouse' for child in child_list]))


def determine_shared_custody(questions_dict):
    child_list = get_children(questions_dict)
    return any([child['child_live_with'] == 'Lives with both'
         for child in child_list])


def determine_split_custody(questions_dict):
    child_list = get_children(questions_dict)
    with_you = 0
    with_spouse = 0
    with_both = 0
    for child in child_list:
        if child['child_live_with'] == 'Lives with you':
            with_you += 1
        elif child['child_live_with'] == 'Lives with spouse':
            with_spouse += 1
        elif child['child_live_with'] == 'Lives with both':
            with_both += 1
    return (with_you > 0 and (with_spouse + with_both > 0) or
            with_spouse > 0 and (with_you + with_both > 0))


def determine_child_over_19_supported(questions_dict):
    try:
        children_over_19 = float(questions_dict.get('number_children_over_19', 0))
    except ValueError:
        children_over_19 = 0

    support = json.loads(questions_dict.get('children_financial_support', '[]'))
    has_children_of_marriage = questions_dict.get('children_of_marriage', '') == 'YES'
    return (len(support) > 0 and children_over_19 > 0 and
            'NO' not in support and has_children_of_marriage)


def determine_missing_undue_hardship_reasons(questions_dict):
    claiming_undue_hardship = questions_dict.get('claiming_undue_hardship', '') == 'YES'
    if claiming_undue_hardship:
        at_least_one_of = ["claimant_debts", "claimant_expenses", "supporting_non_dependents", "supporting_dependents",
                           "supporting_disabled", "undue_hardship"]
        for question in at_least_one_of:
            value = questions_dict.get(question)
            if value:
                try:
                    items = json.loads(value)
                    for item in items:
                        for key in item:
                            if item[key]:
                                return False
                except json.JSONDecodeError:
                    if value:
                        return False

    return True
