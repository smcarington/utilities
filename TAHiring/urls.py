
from django.conf.urls import url, include, patterns
from django.contrib import admin
from . import views

urlpatterns = [
    # TA Application Form
    url(r'^ta_application/personal$', views.application_form_personal, name='application_form_personal'),
    url(r'^ta_application/courses$', views.application_form_courses, name='application_form_courses'),
    url(r'^ta_application/availability/(?P<term>\w+)$', views.application_form_availability, name='application_form_availability'),
    url(r'^ta_application/complete$', views.application_complete, name='application_complete'),
    # Admin Reviewing TAs
    url(r'^ta_application/review/$', views.review_applicants, name='review_applicants'),
    url(r'^ta_application/review/(?P<tapk>\d+)$', views.review_applicants, name='review_applicants'),
    url(r'^ta_application/review/course/schedule/(?P<course_pk>\d+)$', views.review_course_schedule, name='review_course_schedule'),
    url(r'^ta_application/review/course/table/(?P<course_pk>\d+)$', views.review_course_table, name='review_course_table'),
    url(r'^ta_application/assign_ta/$', views.assign_ta_to_tutorial, name='assign_ta'),
    # Offers
    url(r'^ta_application/confirm_offer/(?P<uidb64>[0-9A-Za-z\-]+)/(?P<token>[0-9A-za-z]+)$', views.confirm_offer, name='confirm_offer'),
]
