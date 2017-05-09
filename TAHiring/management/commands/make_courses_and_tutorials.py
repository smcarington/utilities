from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError

from TAHiring.models import *
import logging

class Command(BaseCommand):
    """ A command for uploading marks. Expects a comma separated list
        student_number, score
    """

    def add_arguments(self, parser):
        parser.add_argument('filename')
        parser.add_argument('--log', dest='log')

    def handle(self, *args, **options):
        DOW_DICTIONARY = {
            'Monday'   : 'M',   
            'Tuesday'  : 'T',   
            'Wednesday': 'W',   
            'Thursday' : 'R',   
            'Friday'   : 'F',   
            'Saturday' : 'S',   
            'Sunday'   : 'U',   
        }
        if options['log']:
            logging.basicConfig(filename=options['log'], level=logging.DEBUG)

        with open(options['filename']) as e_file:
            lines = [line.strip().split(',') for line in e_file]

        for user in lines:
            [course_code, meeting, dow, start, end] = [item.strip() for item in user]

            dow = DOW_DICTIONARY[dow]
            
            if "TUT" in meeting: #Only work with tutorials
                # Extract the important data from the strings
                term     = course_code[-1]
                tut_name = meeting[3:]
                course, c_cre = Course.objects.get_or_create(
                    course_code = course_code,
                    term        = term
                )
                CourseTutorial.objects.create_tutorials(
                    name = tut_name,
                    course = course,
                    day = dow,
                    start = start,
                    end = end
                )
                print('Created Tutorial TUT{} for {} from {} to {}'.format(
                    tut_name, course_code, start, end)) 
