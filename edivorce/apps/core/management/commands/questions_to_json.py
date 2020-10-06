import csv
import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Export Questions.csv as Questions.json'

    def handle(self, *args, **options):
        csv_path = os.path.join(settings.PROJECT_ROOT.parent, 'Question.csv')
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            dicts = [line for line in reader]

        json_path = os.path.join(settings.PROJECT_ROOT, 'edivorce/fixtures/Question.json')
        with open(json_path, 'w') as file:
            json_questions = []
            for line in dicts:
                question_dict = {
                    "fields": {
                        "name": line['name'],
                        "description": line['description'],
                        "summary_order": int(line['summary_order']),
                        "required": line['required'],
                    },
                    "model": "core.question",
                    "pk": line['key']
                }
                if line['conditional_target']:
                    question_dict["fields"]["conditional_target"] = line['conditional_target']
                    reveal_response = line['reveal_response']
                    if reveal_response.lower() == 'true':
                        reveal_response = reveal_response.capitalize()
                    question_dict["fields"]["reveal_response"] = reveal_response
                json_questions.append(question_dict)
            file.write(json.dumps(json_questions, indent=4))
            file.write('\n')
