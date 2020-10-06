import csv
import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Export Questions.json as Questions.csv'

    def handle(self, *args, **options):
        json_path = os.path.join(settings.PROJECT_ROOT, 'edivorce/fixtures/Question.json')
        with open(json_path, 'r') as file:
            all_lines = [line for line in file.readlines()]
            questions = json.loads('\n'.join(all_lines))
            print(questions)

        csv_path = os.path.join(settings.PROJECT_ROOT.parent, 'Question.csv')
        with open(csv_path, 'w') as file:
            field_names = ['description', 'key', 'name', 'summary_order', 'required', 'conditional_target', 'reveal_response']
            writer = csv.DictWriter(file, field_names)
            writer.writeheader()
            dicts = []
            for question in questions:
                dicts.append({
                    'description': question['fields']['description'],
                    'key': question['pk'],
                    'name': question['fields']['name'],
                    'summary_order': question['fields']['summary_order'],
                    'required': question['fields'].get('required', ''),
                    'conditional_target': question['fields'].get('conditional_target', ''),
                    'reveal_response': question['fields'].get('reveal_response', ''),
                })
            writer.writerows(dicts)
