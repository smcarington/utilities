from django import template
from django.conf import settings
from TAHiring.models import *

import TAHiring.helper_functions as hf


register = template.Library()

@register.inclusion_tag('TAHiring/schedule.html')
def availability_table(selected):
    """ An inclusion tag used to create the availability table. Requires
        settings.TIME_WINDOW, which describes the gap between time slots in
        minutes. For example, if TIME_WINDOW = 15, then 15 minute gaps are used.
        Input: 
        - title (String) with the table title
        - selected (array of strings) containing the session data if previously
          selected. For example, ["M1230", "T1430"].
    """

    DAYS, HOURS = hf.generate_days_and_time()

    return {
            'times'   : HOURS,
            'days'    : DAYS,
            'selected': selected,
    }

@register.inclusion_tag('TAHiring/course_tutorial_schedule.html')
def generate_course_review_table(course, tutorials, tas):
    """ Creates the table of tutorials.
    """

    DAYS, HOURS = hf.generate_days_and_time()

    return {
            'times'   : HOURS,
            'days'    : DAYS,
            'tutorials': tutorials,
            'tas' : tas,
    }

@register.simple_tag
def html_for_ta_output(tas):
    """ Returns different html output depending on the number of tas which can
        occupy the tutorial.
    """

    if len(tas) == 1:
        ret_str = "1 available TA "
    else:
        ret_str = "{} available TAs".format(len(tas))

    return ret_str

@register.inclusion_tag('TAHiring/generate_course_review_table_td.html')
def generate_course_review_table_td(ts_string, tut_list, tas):
    """ Generated td specific entry for course_review_table.
    """
    # There are several things we need to check. 
    # 1. Is there a tutorial during the given timeslot? If so, how many. Show
    #    this information
    # 2. Are those tutorials filled? If so, color them differently
    # 3. The overlay (to be toggled by js) showing the number of TAs compatible
    #    with that tutorial
    # 4. The modal overlay with that information
    #  
    # We want to handle as much as the logic here rather than the template,
    # which is harder to do
    
    has_tutorial  = False
    num_tutorials = 0
    num_filled    = 0
    is_first      = False
    is_last       = False
    num_tas       = None
    tut_string    = ''
    assigned      = []

    # Is there a tutorial during this time?
    tut_ts_strings = [tut.timeslot.to_string() for tut in tut_list]
    if ts_string in tut_ts_strings:
        has_tutorial = True
        num_tutorials = tut_ts_strings.count(ts_string)

        # Now convert ts_string to timeslot, so we can work in the other
        # direction
        timeslot = TimeSlot.objects.get_timeslot_by_string(ts_string)

        dow = ts_string[0]
        tod = ts_string[1:]
        tuts=tut_list.filter(
                timeslot__day_of_week = settings.DOW_DICTIONARY[dow],
                timeslot__time_of_day = tod
        )

        tut_pks = []

        for tut in tuts:
            if tut.ta:
                num_filled +=1
            if tut.is_first:
                is_first = tut
            if tut.is_last:
                is_last  = tut
            tut_pks.append(str(tut.pk))

        # Cheating, but assuming all the same
        num_tas=tuts[0].get_ta_in_list(tas)
        assigned = [tut.ta.full_name for tut in tuts.filter(ta__isnull=False)]
        # Get the list of tutorial pks for this timeslot, but write it as a
        # string so can be passed back and forth from html
        tut_string = ",".join(tut_pks)

    return {
            'ts_string'    : ts_string,
            'has_tutorial' : has_tutorial,
            'num_tutorials': num_tutorials,
            'num_filled'   : num_filled,
            'is_first'     : is_first,     
            'is_last'      : is_last,     
            'num_tas'      : num_tas,     
            'tut_string'   : tut_string,
            'assigned'     : assigned,
    }

@register.simple_tag
def array_to_string(the_array):
    """Turns an array into a string """

    # Ensure everything in the array is a string
    str_array = [str(item) for item in the_array]
    return ",".join(str_array)

@register.filter
def is_selected(selected, dow, tod):
    """ checks if the timeslot is among the selected slots """
    return str(dow)+str(tod) in selected
