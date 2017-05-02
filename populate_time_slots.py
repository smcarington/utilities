from django.conf import settings
import datetime as dt

from TAHiring.models import TimeSlot

DOW_CHOICES = {
        'M': 0,
        'T': 1,
        'W': 2,
        'R': 3,
        'F': 4,
}
START_TIME = "0800"
END_TIME   = "1900"
TIME_FORMAT = "%H%M"
INTERVAL = settings.TIME_INTERVAL

try:
    DT_START = dt.datetime.strptime(START_TIME, TIME_FORMAT).time()
    DT_END   = dt.datetime.strptime(END_TIME, TIME_FORMAT).time()
except Exception as e:
    print('Invalid START_TIME or END_TIME parameter. Error: {}'.format(e))

cur_time = DT_START
HOURS = [cur_time.strftime(TIME_FORMAT)]
done = False

# Generate the list of times
while not done:
    cur_time = (dt.datetime.combine(dt.date.today(), cur_time) + dt.timedelta(minutes=INTERVAL)).time()
    HOURS.append(cur_time.strftime(TIME_FORMAT))

    if cur_time >= DT_END:
        done = True

# Do row by row. In this case, the outer loop is time and the inner loop is days. This makes it
# nice for formatting the table 
for time in HOURS:
    for dow in DOW_CHOICES:
        ts = TimeSlot(
                day_of_week = DOW_CHOICES[dow],
                time_of_day = time
        )
        ts.save()
