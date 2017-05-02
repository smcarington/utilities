import datetime as dt

def generate_days_and_time(START_TIME = "0900", END_TIME = "1900"):
    """ Helper method used to generate raw data for making the availability
        schedule.
    """

    # We will now generate the tables by iterating over both the days of the week, and 
    # the available time slots
    DAYS = ['M','T','W','R','F']
    # Todo: Give admin access to this
    time_data = {
            "start_time": START_TIME,
            "end_time": END_TIME,
            "time_format": "%H%M",
            "time_interval": 30,
    }

    try:
        DT_START = dt.datetime.strptime(
                time_data['start_time'],
                time_data['time_format']
        ).time()
        DT_END   = dt.datetime.strptime(
                time_data['end_time'], 
                time_data['time_format']
        ).time()
    except Exception as e:
        print('Invalid START_TIME or END_TIME parameter. Error: {}'.format(e))

    cur_time = DT_START
    HOURS = [cur_time.strftime(time_data['time_format'])] # Keeps track of the time gaps (not necess hours)
    done = False

    # Generate the list of times
    while not done:
        cur_time = (dt.datetime.combine(dt.date.today(), cur_time) +
                dt.timedelta(minutes=time_data['time_interval'])).time()
        HOURS.append(cur_time.strftime(time_data['time_format']))

        if cur_time >= DT_END:
            done = True

    return DAYS, HOURS


