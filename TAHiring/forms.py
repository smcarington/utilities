from django import forms

from .models import *

class PersonalInfoForm(forms.ModelForm):
    
    class Meta:
        model = TAData
        fields = ('first_name', 'last_name', 'utorid', 'email', 
                'phone', 'education', 'prev_courses', 'other_exp')

class CourseForm(forms.ModelForm):
    attrs = {'style': 'width: 200px; height: 400px'}
    courses = forms.ModelMultipleChoiceField(
            widget=forms.SelectMultiple(attrs), 
            queryset=Course.objects.all(),
            help_text = "Select all that apply",
    )

    class Meta:
        model = TAData
        fields = ('num_tut_int', 'multi_class', 'summer_ta')
        help_texts = {
                'num_tut_int': ("Indicate the number of tutorials in which you "
                                "are interested"),
                'multi_class': ("Select if you're available to TA for multiple "
                                "different classes."),
                'summer_ta': ("Indicate if you are interested in TAing during "
                              "the summer")
        }
        labels = {
                'courses': "Qualified Courses"
        }
