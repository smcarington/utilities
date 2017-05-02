from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from django.core.validators import MaxValueValidator, MinValueValidator

import datetime as dt
import re


class TAData(models.Model):
    """ Stores most TA Data. More variable information is lnked to TAData
        through foreign key relationships. For example, TA availabilty and
        courses the TA is interested in will be separate models linked to the TA
        through a foreign key relationship.
    """

    # Validators: phone_regex used to validate the phone number,
    #             tutorial_num used to validate number of tutorials
    def phone_validator(value):
        pattern = re.compile(r'^\+?1?\d{9,15}$')
        if not pattern.match(value):
            raise ValidationError("Invalid Phone Number")

    # Changed for built-in validators (04/27/17)
    #def tutorial_num(value):
    #    if value <= 0 or value > 4:
    #        raise ValidationError(
    #                _('%(value) is not a valid number of tutorials'),
    #                params = {'value': value},
    #        )

    # Education choices for the model below.
    EDU_CHOICES = (
                        ('UG2', 'Second Year Undegraduate'),
                        ('UG3', 'Third Year Undegraduate'),
                        ('UG4', 'Fourth Year Undegraduate'),
                        ('MAS', 'Masters'),
                        ('PHD', 'PhD'),
                  )
    
    first_name   = models.CharField(max_length=20, verbose_name="First Name")
    last_name    = models.CharField(max_length=20, verbose_name="Last Name")
    utorid       = models.CharField(max_length=10, verbose_name="UTORid")
    email        = models.EmailField()
    phone        = models.CharField(
        validators=[phone_validator], 
        max_length=15
    )
    education    = models.CharField(
            choices = EDU_CHOICES, 
            max_length=3,
            verbose_name="Education"
    )
    prev_courses = models.TextField(
            blank=True, 
            verbose_name="Previous Courses TA'ed"
    )
    other_exp    = models.TextField(
            blank=True,
            verbose_name = "Other Experience"
    )
    num_tut_int  = models.IntegerField(
            validators=[
                MinValueValidator(1),
                MaxValueValidator(4)
            ],
            blank=True, null=True,
            verbose_name = "Number of Tutorials"
    )
    multi_class  = models.BooleanField(
            default=True, blank=True,
            verbose_name = "TA Multiple Classes"
    )
    summer_ta    = models.BooleanField(
            default=True, blank=True,
            verbose_name = "Summer TAing"
    )

    def update_info(self, info_dict):
        """ Used to update personal information. personal_dict should be a
            dictionary with keys related to the model.
        """
        try:
            for key, value in info_dict.items():
                setattr(self, key, value)
            self.save()
        except Exception as e:
            print(e)

    def availability_as_string(self):
        """ Gets the TA's availability, but returns the list in the format
        ["M0930", "R1500", ... ].
        """
        avails = self.availability.select_related('timeslot').all()
        time_as_str = [avail.timeslot.to_string() for avail in avails]

        return time_as_str

    class Meta:
        verbose_name = "TA Information"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{last}, {first}".format(
            last  = self.last_name,
            first = self.first_name)

class TimeSlotManager(models.Manager):
    """ Adds custom manager functions to the timeslot model
    """

    def get_timeslot_by_string(self,ts_string):
        """ Gets the current time slot using the given string. Currently only
            works with %H%M format. Should be of form M0930
        """
        DOW_DICTIONARY = {
            'M': 0,
            'T': 1,
            'W': 2,
            'R': 3,
            'F': 4,
            'S': 5,
            'U': 6,
        }
        dow = ts_string[0]
        tod = ts_string[1:]

        return super().get_queryset().get(
                day_of_week = DOW_DICTIONARY[dow],
                time_of_day = tod)

class TimeSlot(models.Model):
    """ Abstract model for time slots. Keeps track of day of week and the start
        time. End time is based off settings.TIME_WINDOW (minutes)
    """
    # Time validator. Ensures that input time is 4-char string in 24 hour
    # notation. For example, 1730
    def time_validator(value):
        TIME_FORMAT = "%H%M"
        try:
            dt.datetime.strptime(value, TIME_FORMAT).time()
        except Exception as e:
            raise ValidationError()

    # Choices for day_of_week field
    DOW_CHOICES = (
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    )

    # Python datetime, Monday = 0, Sunday = 6
    day_of_week = models.IntegerField(
        choices=DOW_CHOICES, 
        validators=[
            MinValueValidator(0),
            MaxValueValidator(6)
        ]
    )

    # Encoded in 24 hour time, so 7:30pm is 1930
    time_of_day = models.CharField(
        max_length=4,
        validators = [time_validator]
    )

    objects = TimeSlotManager()

    def to_string(self):
        DOW_DICTIONARY = {
            '0': 'M',
            '1': 'T',
            '2': 'W',
            '3': 'R',
            '4': 'F',
            '5': 'S',
            '6': 'U',
        }
        return DOW_DICTIONARY[str(self.day_of_week)]+self.time_of_day

    def __str__(self):
        return "{dow} {tod}".format(
            dow = self.day_of_week,
            tod = self.time_of_day
        )

class TAAvailability(models.Model):
    """ Inherits TimeSlot. Tracks TA availability. One row per opening
    """
    ta = models.ForeignKey(TAData, related_name="availability")
    timeslot = models.ForeignKey(TimeSlot, related_name="ta_availability", null=True)
    is_new = models.BooleanField(default=False)

    def set_new(self, is_new):
        self.is_new = is_new
        self.save()

    class Meta:
        verbose_name = "TA Availability"
        verbose_name_plural = "TA Availabilities"

    def __str__(self):
        return "{ln},{fn}: {ts}".format(
                ln=self.ta.last_name,
                fn=self.ta.first_name,
                ts=self.timeslot.to_string())

class Course(models.Model):
    """ Tracks course information. Currently only set up to handle tutorials,
        but lecture slots could easily be added for extendability.
    """
    # Should be of form AAAXXX, like MAT102 or STA257
    course_code = models.CharField(max_length=6)

    class Meta:
        verbose_name = "Course"

    def __str__(self):
        return self.course_code

class TACourseInterest(models.Model):
    """ Keeps track of what courses a TA is interested in.
    """
    course = models.ForeignKey(Course, related_name="tas_interested")
    ta     = models.ForeignKey(TAData, related_name="courses_interested")
    is_new = models.BooleanField(default=False)

    def set_new(self, the_bool = True):
        """Updates the boolean value of is_new"""
        self.is_new = the_bool
        self.save()

    def __str__(self):
        return "{ta}: {course}".format(
                ta = self.ta.first_name + ", " + self.ta.last_name,
                course = self.course.course_code
        )

class Course_Tutorial(models.Model):
    """ Tracks tutorials for a course. One row per tutorial. Has a foreign key
        relationship to Course
    """
    name     = models.CharField(max_length=4) # 0104, will assume TUT prefix
    course   = models.ForeignKey(Course, related_name="tutorials")
    timeslot = models.ForeignKey(TimeSlot, related_name="tutorials")
    ta       = models.ForeignKey(TAData, related_name="tutorials", null=True)

    class Meta:
        verbose_name = "Tutorial"

    def __str__(self):
        return "{course}: TUT{name}".format(
            course = self.course.course_code,
            name = self.name
        )
