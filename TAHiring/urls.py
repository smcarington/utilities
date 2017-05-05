
from django.conf.urls import url, include, patterns
from django.contrib import admin
from . import views

urlpatterns = [
    # TA Application Form
    url(r'^ta_application/personal$', views.application_form_personal, name='application_form_personal'),
    url(r'^ta_application/courses$', views.application_form_courses, name='application_form_courses'),
    url(r'^ta_application/availability$', views.application_form_availability, name='application_form_availability'),
    url(r'^ta_application/complete$', views.application_complete, name='application_complete'),
    # Admin Reviewing TAs
    url(r'^ta_application/review/$', views.review_applicants, name='review_applicants'),
    url(r'^ta_application/review/(?P<tapk>\d+)$', views.review_applicants, name='review_applicants'),
    url(r'^ta_application/review/course/(?P<course_pk>\d+)$', views.review_course, name='review_course'),
]
