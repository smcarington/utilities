from django_tables2 import tables, Column, Table
from django.utils.html import format_html

from .models import *

class TA_List_Table(Table):
    """ Used for displaying TAs. Called from views.review_applicants
    """
    last_name  = Column()
    first_name = Column()
    education  = Column()
    courses    = Column(
            empty_values=(),
            verbose_name = "Qualified Courses"
    ) # Displays qualified courses

#    see_details = Column(empty_values=()) #Click for TA details

    class Meta:
        models = TAData
        attrs = {'class': 'paleblue mymodal-click'}
        fields = ['last_name', 'first_name', 'education']
        row_attrs = {'data-id': lambda record: record.pk}

    def render_courses(self, value, record):
        """ Pull the TA's list of qualified courses. 'record' is a TAData object.
        """
        course_list = record.courses_interested.all().values_list('course__course_code', flat=True)
        
        return format_html(
                "<span>{}</span>",
                ", ".join([str(course) for course in course_list])
        )
