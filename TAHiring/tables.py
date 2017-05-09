from django_tables2 import tables, Column, Table
from django.utils.html import format_html

from .models import *

class TA_List_Table(Table):
    """ Used for displaying TAs. Called from views.review_applicants
    """
    last_name  = Column(orderable=True)
    first_name = Column()
    education  = Column()
    courses    = Column(
            empty_values=(),
            verbose_name = "Qualified Courses"
    ) # Displays qualified courses
    assigned   = Column(
            empty_values=(),
            verbose_name = "Assigned Tutorials"
    ) # Gets which tutorials the TA has been assigned

#    see_details = Column(empty_values=()) #Click for TA details

    class Meta:
        models = TAData
        attrs = {'class': 'paleblue mymodal-click'}
        fields = ['last_name', 'first_name', 'education']
        row_attrs = {'data-id': lambda record: record.pk}
        order_by = ['last_name', 'first_name']

    def render_courses(self, value, record):
        """ Pull the TA's list of qualified courses. 'record' is a TAData object.
        """
        course_list = record.courses_interested.all().values_list('course__course_code', flat=True)
        
        return format_html(
                "<span>{}</span>",
                ", ".join([str(course) for course in course_list])
        )

    def render_assigned(self, value, record):
        """ See which tutorials have been assigned to the TA. Makes use of the
        TAData model method tutorials_as_string
        """

        return format_html(
                "<span>{}</span>",
                record.tutorials_as_string()
        )

class CourseTutorialTable(Table):
    tutorial = Column()
    day      = Column()
    start    = Column(verbose_name = "Start Time")
    end      = Column(verbose_name = "End Time")
    ta       = Column(empty_values=(), verbose_name = "Assigned TA")

    class Meta:
        attrs = {'class': 'paleblue mymodal-click'}
        order_by = ['tutorial']

    def render_ta(self, value, record):
        """ This will change depending on whether ta is null. If ta is null,
        give a selection box for available TAs. If not null, show the TA and
        give the option to unassign the TA"""

        if value: #ta is not null
            return format_html(
                    (
                        "<span>{taname}</span> <a data-ta={tapk} data-tut={tutpk}"
                        " href=javascript:void() class='ta-unassign'>(unassign)</a>"
                    ),
                    taname=value.full_name,
                    tapk = value.pk,
                    tutpk=record['tut_pk']
            )
        else:
            select_template = (
                "<select data-tut='{tutpk}' id='ta-select'"
                "class='form-control'> \n {opts} </select> "
            )
            options = "<option selected disabled hidden style='display: none' value=''></option> \n"
            for ta in record['all_tas']:
                select_opt = (
                    "<option value='{tapk}' >{tafn}</option>"
                    .format(
                        tapk  = ta.pk,
                        tafn  = ta.full_name
                    )
                )
                options += select_opt + "\n"

            ret_str = select_template.format(
                tutpk=record['tut_pk'],
                opts=options)

            return format_html(ret_str)
