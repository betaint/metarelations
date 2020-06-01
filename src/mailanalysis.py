"""
:synopsis: Parsing sender and datum from emails in mbox format.
"""

# standard library imports
import collections
import datetime

# third party imports
from matplotlib import pyplot
import numpy


def parse_mails(mail, THRESHOLD):
    """Parse messages in mail and extract certain metadata.

    :param mailbox.mbox mail: The mailbox being parsed
    :param int THRESHOLD: The minimum number of emails for each sender to be
    taken into account
    :returns: A tuple of two dictionaries with email metadata
    :rtype: tuple(dict(str: int), dict(str: list(datetime.datetime)))
    """

    # Initialize several empty dictionaries
    mails_per_address = collections.defaultdict(int)
    mails_per_address_with_threshold = collections.defaultdict(int)
    datetimes_per_sender = collections.defaultdict(list)
    datetimes_per_sender_with_threshold = collections.defaultdict(list)

    for message in mail:
        sender = message['From']
        datum = message['Date']

        # If 'sender' or 'datum' are missing, continue with the next iteration
        # of the for-loop
        if sender is None or datum is None:
            continue

        # Extract the email address from 'sender' and increment the counter for
        # this address. Account for the case that 'sender' consists of an email
        # address which is not enclosed in <>
        if '@' not in sender:
            continue

        sub_strings = sender.split('@')
        if len(sub_strings) != 2:
            continue

        if '<' in sender and '>' in sender:
            sender = sender[sender.find(' <') + 2:sender.find('>')]
        sender = sender.lower()
        mails_per_address[sender] += 1

        date_string = datum[:datum.find(':') + 6]

        datetime_obj = parse_datetime(date_string)
        datetimes_per_sender[sender].append(datetime_obj)

    # Use a threshold, previously specified in the configuration file, for the
    # number of emails from which on a sender is taken into account
    for address in mails_per_address:
        if mails_per_address[address] >= THRESHOLD:

            mails_per_address_with_threshold[address] = \
                mails_per_address[address]
            datetimes_per_sender_with_threshold[address] = \
                datetimes_per_sender[address]

    return mails_per_address_with_threshold, datetimes_per_sender_with_threshold


def parse_datetime(datum):
    """Parse date and timestamp.

    :param str datum: The datum being parsed
    :returns: A datetime object
    :rtype: datetime.datetime
    :raises ValueError: if the datum does not match the specified formats
    """

    # Remove unnecessary information and strip leading and trailing whitespace
    if ' +' in datum:
        datum, _ = datum.split(' +')
    datum.strip()

    # Check date and timestamp formats according to 'format_string'
    for format_string in ('%a, %d %b %Y %H:%M:%S', '%a, %d %b %Y %H:%M',
                          '%d %b %Y %H:%M:%S', '%d %b %Y %H:%M'):
        try:
            datetime_obj = datetime.datetime.strptime(datum, format_string)
            break
        except ValueError:
            continue
    else:
        raise ValueError(f'date {datum} does not match any supported format')

    return datetime_obj


def plot_received_mails_per_address(mails_per_address, THRESHOLD, output):
    """Plot the number of received emails for each address in a barplot.

    :param dict mails_per_address: Number counts of emails for each address
    :param int THRESHOLD: The minimum value to take a sender into account
    :param str output: The directory to save the output to
    """

    number_of_addresses = len(mails_per_address)
    ind = numpy.arange(number_of_addresses)
    width = 0.4

    fig, ax = pyplot.subplots(figsize=(8, 6))
    ax.bar(ind, mails_per_address.values(), width)
    ax.set_xticks(ind + width / 2)
    ax.set_xticklabels(mails_per_address.keys(), rotation=90)
    ax.set_xlabel("Address")
    ax.set_ylabel("Number of Mails")
    ax.set_title("Received Mails per Address")
    fig.tight_layout(pad=0.4, w_pad=0.5, h_pad=0.8)
    fig.savefig(output + 'received_mails_per_address_threshold_' + str(
        THRESHOLD) + '.svg')
