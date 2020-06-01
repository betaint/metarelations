"""
:synopsis: Engineering, aggregation and minmax-scaling of features.
"""

# standard library imports
import collections

# third party imports
import pandas
from sklearn import preprocessing


def aggregate_dataframe(mails_per_sender, datetimes_per_sender):
    """Engineer features and aggregate them in a dataframes.

    :param dict mails_per_sender: A dictionary with email counts for each sender
    :param dict datetimes_per_sender: A dictionary with datetime objects for
    each sender
    :returns: A dataframe with aggregated features
    :rtype: pandas.DataFrame
    """

    average_timestamps = average_timestamps_in_seconds(
        datetimes_per_sender)
    average_weekdays = weekday_average(datetimes_per_sender)

    aggregation = {'Mail Count': mails_per_sender,
                   'Average Timestamp': average_timestamps,
                   'Average Weekday': average_weekdays}

    return pandas.DataFrame(aggregation)


def average_timestamps_in_seconds(datetimes_per_sender):
    """ Calculate the seconds since midnight for each sender.

    :param dict datetimes_per_sender: A dictionary with a list of datetime
    objects for each sender
    :returns: The average timestamp for each sender in seconds since midnight
    :rtype: dict(str: int)
    """

    seconds_total = 0
    timestamps_in_seconds = collections.defaultdict(int)

    for sender in datetimes_per_sender:
        number_of_timestamps = len(datetimes_per_sender[sender])
        for t in datetimes_per_sender[sender]:
            seconds_of_timestamp = t.hour * 3600 + t.minute * 60 + t.second
            seconds_total += seconds_of_timestamp
        seconds_average = round(seconds_total / number_of_timestamps)
        timestamps_in_seconds[sender] = seconds_average

    return timestamps_in_seconds


def weekday_average(datetime_per_sender):
    """Calculate the weekday average of each sender.

    :param dict datetime_per_sender: A dictionary with a list of datetime
    objects for each sender
    :returns: The average weekday for each sender
    :rtype: dict(str: int)
    """

    # Average over the integers representing the weekdays and round the result
    # to the nearest integer
    average_weekday_per_sender = collections.defaultdict(int)

    for sender in datetime_per_sender:
        datum_count = len(datetime_per_sender[sender])
        weekdays = [datum.weekday() for datum in datetime_per_sender[sender]]
        average_weekday_per_sender[sender] = round(sum(weekdays) / datum_count)

    return average_weekday_per_sender


def weekday_maximum(datetime_per_sender):
    """Calculate the weekday maximum of each sender.

    :param dict datetime_per_sender: A dictionary with a list of datetime
    objects for each sender
    :returns: The maximum weekday for each sender
    :rtype: dict(str: int)
    """

    max_weekday_per_sender = collections.defaultdict(int)

    for sender in datetime_per_sender:
        weekdays = [datum.weekday() for datum in datetime_per_sender[sender]]
        counter = collections.Counter(weekdays)
        # x[1] is the second element of each tuple item in counter.items()
        weekday, maximum = max(counter.items(), key=lambda x: x[1])

        # Account for the possibility that two or more weekdays have the same
        # number count in counter and average over them, rounding to the nearest
        # integer
        key_set = {key for key, val in counter.items() if val == maximum}
        if len(key_set) >= 2:
            weekday = 0
            for key in key_set:
                weekday += key
            weekday = round(weekday / len(key_set))

        max_weekday_per_sender[sender] = weekday

    return max_weekday_per_sender


def feature_scaling(dataframe):
    """Apply minmax-scaling to all features in a dataframe.

    :param pandas.DataFrame dataframe: A pandas.DataFrame with unscaled features
    :returns: A pandas.DataFrame with scaled features
    :rtype: pandas.DataFrame
    """

    scaled_columns = preprocessing.minmax_scale(dataframe)
    scaled_df = pandas.DataFrame(scaled_columns, index=dataframe.index,
                                 columns=dataframe.columns)

    return scaled_df
