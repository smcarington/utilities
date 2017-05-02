from django import template
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


@register.filter
def is_selected(selected, dow, tod):
    """ checks if the timeslot is among the selected slots """
    return str(dow)+str(tod) in selected
