from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_text
from django.template import loader
from django.contrib.sites.shortcuts import get_current_site

from .forms import *
from .models import *
from .tables import *
from .tokens import confirm_offer_token

import TAHiring.helper_functions as hf

# -------- Application Form (fold) -------- #

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
                return redirect(
                        'application_form_availability', 
                        term='Fall'
                    )
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

def application_form_availability(request, term="Fall"):
    """ This view handles the availability selection. Uses a custom form and
        javascript to handle filling in the form. Note that session data is
        stored in an array of strings, of the form "M1730" for Monday at 5:30pm
    """
    if term == "Fall":
        next_call = "availability_spring"
        past_call = "courses"
        header    = "Fall Availability"
        session_name = "availability_fall"
    elif term == "Spring":
        next_call = 'complete'
        past_call = 'availability_fall'
        header    = "Spring Availability"
        session_name = "availability_spring"

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
        cur_avail = TAAvailability.objects.filter(ta=ta, term=term[0])
        cur_avail.update(is_new=False)
        for data in new_selected:
            cur_ts = TimeSlot.objects.get_timeslot_by_string(data)
            obj, created = TAAvailability.objects.get_or_create(
                    ta       = ta,
                    timeslot = cur_ts,
                    term     = term[0]
            )
            obj.set_new(True)

        # Delete anything that wasn't changed
        cur_avail.filter(is_new=False).delete()

        # Store everything in session data
        request.session[session_name] = new_selected

        if next_page == 'courses':
            redirect_url = reverse('application_form_courses')
        elif next_page == 'availability_spring':
            redirect_url = reverse(
                'application_form_availability',
                kwargs={"term":"Spring"}
            )
        elif next_page == 'availability_fall':
            redirect_url = reverse(
                'application_form_availability', 
                kwargs={"term":"Fall"}
            )
        else:
            redirect_url = reverse('application_complete')

        return HttpResponse(redirect_url)

    return render(
        request, 
        'TAHiring/application_availability.html',
        {
            'next'  : next_call,
            'prev'  : past_call,
            'header': header,
            'term'  : term,
        },
    )

def application_complete(request):
    """ Once the application is complete, renders a simple template to show tha
        the application is finished.
    """

    # Delete the session data so that the form can be reused on the same
    # computer
    session_data_names = ['personal', 'courses', 'availability_fall',
    'availability_spring', 'tapk']
    for name in session_data_names:
        del request.session[name]

    return render(
            request,
            'TAHiring/application_complete.html'
    )

# -------- Application Form (end) -------- #

# -------- Application Review (fold) -------- #

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
def review_course_schedule(request, course_pk):
    """ View to examine the tutorials for a particular course. 
    """
    # TODO: Make this a class-based view together with review_course_schedule
    course = Course.objects.get(pk=course_pk)
    list_of_tutorials = CourseTutorial.objects.select_related(
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
            'TAHiring/review_course_schedule.html',
            {
                'course': course,
                'list_of_tutorials': list_of_tutorials,
                'list_of_tas': list_of_tas,
                'courses' : all_courses,
            }
    )

def create_ctt_data(tutorials, tas, course):
    """ Helper function for generating the table data needed to render
    CourseTutorialTable.
    Input: tutorials (list of CourseTutorial objects)
                 tas (list of TAData objects)
              course (Course object)
    Return: array whose items are dictionaries with the fields for
    CourseTutorialTable. These include ['tutorial', 'start', 'end', 'ta'] 
    """
    
    table_data = []

    # Each tutorial has multiple timeslots. Get their names first
    tut_names = tutorials.values_list('name', flat=True)
    tut_names = list(set(tut_names))
    for tut_name in tut_names:
        # Get all the tutorials of the same name, ordered by start time.
        other_tuts = CourseTutorial.objects.filter(
                name=tut_name,
                course=course
        ).order_by('timeslot')

        day = other_tuts[0].timeslot.to_string()[0]
        start_time = other_tuts[0].timeslot.add_time(0)
        end_time   = (other_tuts.reverse()[0]
                .timeslot
                .add_time(settings.TIME_INTERVAL)
        )
        compatible_tas = other_tuts[0].get_ta_in_list(tas)
        ta = other_tuts[0].ta
        tut_pk = other_tuts[0].pk
        
        # Create the row data
        row_data = {
            'tutorial': tut_name,
            'day'     : day,
            'start'   : start_time,
            'end'     : end_time,
            'ta'      : ta,
            'all_tas' : compatible_tas,
            'tut_pk'  : tut_pk,
        }
        table_data.append(row_data)

    return table_data

# NEED TO ADD STAFF PRIVILEGES
def review_course_table(request, course_pk):
    """ Gives a table rendering of the course tutorials """

    # TODO: Make this a class-based view together with review_course_schedule
    course = Course.objects.get(pk=course_pk)
    list_of_tutorials = CourseTutorial.objects.select_related(
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

    table_data = create_ctt_data(list_of_tutorials, list_of_tas, course)
    tutorial_table = CourseTutorialTable(table_data)

    return render(request,
            'TAHiring/review_course_table.html',
            {
                'course': course,
                'list_of_tutorials': list_of_tutorials,
                'list_of_tas': list_of_tas,
                'courses' : all_courses,
                'tutorial_table': tutorial_table,
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
            tuts = CourseTutorial.objects.filter(pk__in=tut_pks)

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

# -------- Application Review (end) -------- #

# -------- Offers (fold) -------- #

def send_offer_email(ta, token=confirm_offer_token):
    """ Helper method for send_offers. Used to send emails to the TAs who have
    been offered a job. Details their courses, tutorials, and provides a
    one-time link for them to accept.
    """

    tutorials = ta.tutorials.all()
    # Get the courses
    courses = (tutorials.values_list('course__course',
            flat=True).distinct().order_by()
    )

    # Create context for the email template
    context = {
        'uid': urlsafe_base64_encode(force_byes(ta.pk)),
        'token' : token,
        'ta' : ta,
        'domain': get_current_site(request).domain
    }

    overall_data = {}
    # Nested dictionary with the important information:
    # For example,
    # overall_data:
    #   'MAT102':
    #       'TUT0102':
    #           'day'   : 'M',
    #           'start' : '0900',
    #           'end  ' : '1000'
    for course in courses:
        tut_names = (CourseTutorial.objects
                .filter(
                    course__course_code=course,
                    ta=ta
                )
                .values_list('name', flat=True)
                .distinct().order_by()
        ) 
        course_data = {}

        for tut_name in tut_names:
            # TODO: Similar code is used in create_ctt_data -- not DRY
            # Get all the tutorials of the same name, ordered by start time.
            other_tuts = CourseTutorial.objects.filter(
                    name=tut_name,
                    course__course_code=course
            ).order_by('timeslot')

            day = other_tuts[0].timeslot.to_string()[0]
            start_time = other_tuts[0].timeslot.add_time(0)
            end_time   = (other_tuts.reverse()[0]
                    .timeslot
                    .add_time(settings.TIME_INTERVAL)
            )
            # Create the row data
            row_data = {
                'day'     : day,
                'start'   : start_time,
                'end'     : end_time,
            }
            course_data[tut_name] = row_data
        
        overall_data[course] = course_data

        # Add our data to context for template rendering
        context['data'] = overall_data

        subject = "UTM TA Offer"
        body = loader.render_to_string('offer_email.html', context)
        email_message = EmailMultiAlternatives(
            subject, 
            body,
            settings.DEFAULT_FROM_EMAIL, 
            [ta.email]
        )

        email_message.send()

def send_offers(request, confirmed=False):
    """ Sends the offers but offers a chance to validate the information.
    In particular, shows any tutorials which were not filled.
    Input: confirmed (Boolean, default False) 
    """

    if confirmed:
        pass
    else: # Send the offers
        tutorials = CourseTutorial.objects.prefetch_related('ta').all()
        ta_pks = tutorials.values_list('ta__pk', flat=True)
        tas  = TAData.objects.prefetch_related('tutorials').filter(pk__in=ta_pks)

        for ta in tas:
            send_offer_email(ta)


def confirm_offer(request, uidb64, token):
    """ Confirm an offer by use of a one time link.
    """

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        ta  = TAData.objects.get(pk=uid)
    except Exception as e:
        ta = None

    if ta is not None and confirm_offer_token.check_token(ta, token):
        ta.accept_offer()
        return redirect('offer_accepted')
    else:
        return redirect('invalid_token')

# -------- Offers (end) -------- #
