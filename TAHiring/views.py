from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse

from .forms import *
from .models import *
from .tables import *

import TAHiring.helper_functions as hf

# -------- Application Form (Start) -------- #

def application_form_personal(request):
    """ TA application form for personal information
    """

    next_call = 'courses'
    past_call = ''
    header = "Personal Information"
    next_page = 'personal'

    # If post, then save data and redirect to new page
    if request.method == "POST":
        next_page = request.POST['nextPage']
        form = PersonalInfoForm(request.POST)

        if form.is_valid():
            # Check to see if the form is valid. If so, update the session data.
            # Then check to see if we need to generate the courses or not
            request.session['personal'] = form.cleaned_data
            if 'tapk' in request.session and request.session['tapk']:
                ta = TAData.objects.get(pk=request.session['tapk'])
            else:
                ta = TAData()
            ta.update_info(request.session['personal'])

            request.session['tapk']=ta.pk

            if next_page == 'courses':
                return redirect('application_form_courses')
            else:
                raise Http404("Incorrect redirect")
            
    else: # Get request, so either first time or redirected from courses
        if 'personal' in request.session and request.session['personal']:
            form = PersonalInfoForm(initial=request.session['personal'])
        else:
            form = PersonalInfoForm()

    return render(
        request, 
        'TAHiring/application_form.html',
        {
            'form': form,
            'next': next_call,
            'past': past_call,
            'header': header,
            'step': next_page
        },
    )

def application_form_courses(request):
    # If post, then save data and redirect to new page
    next_call = 'availability'
    past_call = 'personal'
    header = "Qualified Courses"

    if request.method == "POST":
        next_page = request.POST['nextPage']
        form = CourseForm(request.POST)

        if form.is_valid():
            # Check to see if the form is valid. If so, update the session data.
            # Then check to see if we need to generate the courses or not
            list_of_courses = form.cleaned_data['courses']
            ta = TAData.objects.get(pk=request.session['tapk'])

            ta.courses_interested.all().update(is_new = False)
            #Generate the TACourseInterest objects and also serialize them. Delete the changed offers
            for course in list_of_courses:
                taci, created = TACourseInterest.objects.get_or_create(
                        course = course,
                        ta     = ta
                )
                taci.set_new()

            ta.courses_interested.filter(is_new=False).delete()

            # Serialize for session data
            course_list_pk = [course.pk for course in list_of_courses]
            request.session['courses'] = course_list_pk

            if next_page == 'availability':
                return redirect('application_form_availability')
            elif next_page == 'personal':
                return redirect('application_form_personal')
            else:
                raise Http404("Incorrect redirect")
            
    else: # GET request
        if 'courses' in request.session and request.session['courses']:
            initial_data = Course.objects.filter(
                    pk__in=request.session['courses']
            )
            form = CourseForm(initial={'courses': initial_data})
        else:
            form = CourseForm()

    return render(
        request, 
        'TAHiring/application_form.html',
        {
            'form': form,
            'next': next_call,
            'past': past_call,
            'header': header,
        },
    )

def application_form_availability(request):
    """ This view handles the availability selection. Uses a custom form and
        javascript to handle filling in the form. Note that session data is
        stored in an array of strings, of the form "M1730" for Monday at 5:30pm
    """
    next_call = 'complete'
    past_call = 'courses'
    header = "Availability"

    # If post, then save data and redirect to new page
    if request.method == "POST":
        # Set up the data-dictionary
        next_page = request.POST['nextPage']

        # Here we're not using django's built in form processor, but rather
        # using client side code to submit the form data. We'll have to do some
        # validation by hand.

        new_selected = request.POST.getlist('highlighted[]')
        ta = TAData.objects.get(pk=request.session['tapk'])

        # To save time, we're going to see which tutorials changed
        cur_avail = TAAvailability.objects.filter(ta=ta)
        cur_avail.update(is_new=False)
        for data in new_selected:
            cur_ts = TimeSlot.objects.get_timeslot_by_string(data)
            obj, created = TAAvailability.objects.get_or_create(
                    ta       = ta,
                    timeslot = cur_ts
            )
            obj.set_new(True)

        # Delete anything that wasn't changed
        cur_avail.filter(is_new=False).delete()

        # Store everything in session data
        request.session['availability'] = new_selected

        if next_page == 'courses':
            redirect_url = reverse('application_form_courses')
        else:
            redirect_url = reverse('application_complete')

        return HttpResponse(redirect_url)

    return render(
        request, 
        'TAHiring/application_availability.html',
        {
            'next': next_call,
            'prev': past_call,
            'header': header,
        },
    )

def application_complete(request):
    """ Once the application is complete, renders a simple template to show tha
        the application is finished.
    """

    # Delete the session data so that the form can be reused on the same
    # computer
    session_data_names = ['personal', 'courses', 'availability', 'tapk']
    for name in session_data_names:
        del request.session[name]

    return render(
            request,
            'TAHiring/application_complete.html'
    )

# -------- Application Form (End) -------- #

# -------- Application Review (Start) -------- #

# NEED TO ADD STAFF PRIVILEGES
def review_applicants(request, tapk = None):
    """ See the list of applicants. Uses Ajax to load 
    """

    if request.is_ajax():
        # Asking for the TA's schedule, so get the ta and render the schedule
        # using the template
        ta = TAData.objects.get(pk=tapk)
        selected = ta.availability_as_string()
        DAYS, TIMES = hf.generate_days_and_time()

        return render(request,
                'TAHiring/schedule.html',
                {
                    'days': DAYS,
                    'times': TIMES,
                    'selected': selected,
                }
        )

    else:
        # Generate the list of TAs as a table
        list_of_TAs = TAData.objects.all()
       
        ta_table = TA_List_Table(list_of_TAs)

        return render(request,
                'TAHiring/see_list_of_tas.html',
                { 'table': ta_table,
                  'list_of_tas': list_of_TAs,
                }
        )

# NEED TO ADD STAFF PRIVILEGES
def review_course(request, course_pk):
    """ View to examine the tutorials for a particular course. 
    """
    course = Course.objects.get(pk=course_pk)
    list_of_tutorials = Course_Tutorial.objects.select_related(
            'timeslot').filter(course = course)
    # Remember to filter out TAs who are not qualified for this subject.
    ta_pks = (TACourseInterest.objects
                .filter(course=course)
                .values_list('ta__pk', flat=True)
    )
    list_of_tas = (TAData.objects
            .prefetch_related('availability__timeslot', 'courses_interested')
            .filter(pk__in=ta_pks)
    )

    all_courses = Course.objects.all()

    return render(request,
            'TAHiring/review_course.html',
            {
                'course': course,
                'list_of_tutorials': list_of_tutorials,
                'list_of_tas': list_of_tas,
                'courses' : all_courses,
            }
    )

# NEED TO ADD STAFF PRIVILEGES
def assign_ta_to_tutorial(request):
    """ AJAX method for assigning a TA to a tutorial. Takes POST data containing
    the ta_pk and tut_pk.
    """

    if request.method == "POST":
        try:
            ta_pk  = int(request.POST['ta_pk'])
            tut_pks = [int(pkstr) for pkstr in request.POST['tut_pks'].split(',')]
            assign = (request.POST['assign'] == 'true')
            
            ta  = get_object_or_404(TAData, pk=ta_pk)
            tuts = Course_Tutorial.objects.filter(pk__in=tut_pks)

            # Iterate through the tutorials until you find a tutorial that has
            # not been assigned a ta. Assign the ta and break
            if assign:
                for tut in tuts:
                    if not tut.ta:
                        tut.assign_ta(ta)
                        break
            else:
                for tut in tuts:
                    if (tut.ta == ta):
                        tut.remove_ta()
                        break;
            
            ret_str = ("TA {fn} {ln} successfull added to {course}:"
                "TUT{tut}"
                .format(
                    fn = ta.first_name,
                    ln = ta.last_name,
                    course = tut.course.course_code,
                    tut = tut.name
                )
            )
            return HttpResponse(ret_str)

        except Exception as e:
            print(e)
            raise Http404(e)

    else:
        raise Http404('Invalid request')
