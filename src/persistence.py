"""
:synopsis: Plotting persistence and barcode diagrams and calculating clusters.
"""

# standard library imports
import collections

# third party imports
from matplotlib import pyplot
import numpy
import scipy
import ripser
import persim


def product_metric(nd_array_1, nd_array_2):
    """Calculate a product metric.

    :param numpy.array nd_array_1: An array with features
    :param numpy.array nd_array_2: An array with features
    :returns: The product metric of the product topology of a finite number of
    metric spaces and their respective metrics d_n (currently: n=3)
    :rtype: float
    """

    Data = collections.namedtuple('Data', ['mail_count', 'seconds', 'weekday'])

    data_1 = Data(*nd_array_1)
    data_2 = Data(*nd_array_2)

    d_1 = metric_mail_count(data_1.mail_count, data_2.mail_count)
    d_2 = metric_seconds(data_1.seconds, data_2.seconds)
    d_3 = metric_weekday(data_1.weekday, data_2.weekday)

    return numpy.sqrt(d_1 ** 2 + d_2 ** 2 + d_3 ** 2)


def metric_mail_count(mail_count_1, mail_count_2):
    """Calculate the distance between two email counts as an positive integer.

    :param mail_count_1: A positive integer
    :param mail_count_2: A positive integer
    :returns: The absolute valued distance between two email counts
    :rtype: int
    """

    return numpy.absolute(mail_count_1 - mail_count_2)


def metric_seconds(timestamp_1, timestamp_2):
    """Calculate the distance between two points on a 1-sphere in seconds.

    :param int timestamp_1: A timestamp in seconds
    :param int timestamp_2: A timestamp in seconds
    :returns: The distance between two points represented by their
    respective timestamps on a 1-sphere in seconds from midnight
    :rtype: int
    """

    seconds_per_day = 24 * 60 * 60
    return min((timestamp_1 - timestamp_2) % seconds_per_day,
               (timestamp_2 - timestamp_1) % seconds_per_day)


def metric_weekday(weekday_1, weekday_2):
    """Calculate the distance between two weekdays as a positive integer.

    :param weekday_1: A positive integer between 0 and 6
    :param weekday_2: A positive integer between 0 and 6
    :returns: The absolute valued distance between two weekdays
    :rtype: int
    """

    return numpy.absolute(weekday_1 - weekday_2)


def plot_persistence_diagram(dataframe, output, metric=product_metric):
    """Calculate persistence data and plot a persistence diagram.

    :param pandas.DataFrame dataframe: A dataframe with features used to
    calculate the persistence data
    :param str output: The directory to save the output to
    :param metric: The metric used to calculate the persistence data
    :returns: A tuple consisting of all input variables and their respective
    identifiers and a ripser object with the computed persistence data
    :rtype: tuple(tuple(list(numpy.ndarray), list(str)),ripser.ripser)
    """

    # Collect all the for the persistence computation necessary data
    collected_vectors = dataframe.to_numpy()
    identifiers = dataframe.index.to_list()
    collected_data = (collected_vectors, identifiers)

    # Calculate persistence data and the corresponding diagram for the zeroth
    # homology group
    persistence = ripser.ripser(collected_vectors, maxdim=0, metric=metric)
    dgms = persistence['dgms']
    pyplot.figure(figsize=(6, 6))
    pyplot.title('Persistence Diagram')
    persim.plot_diagrams(dgms, show=False)
    pyplot.tight_layout()
    pyplot.savefig(output + 'persistence_diagram_ripser.svg')

    return collected_data, persistence


def plot_barcode_diagram(persistence, output):
    """Plot a barcode diagram.

    :param ripser.ripser persistence: The previously calculated persistence data
    :param str output: The directory to save the output to
    """

    # inspired by https://github.com/scikit-tda/persim/pull/24/commits
    # /67f858f80afb49786c10934e71a1e2cbe42109f9
    dgms = persistence['dgms']
    number_of_dimensions = len(dgms)
    if number_of_dimensions > 0:
        dim = 0
        labels = ["$H_0$", "$H_1$", "$H_2$", "$H_3$"]
        fig, ax = pyplot.subplots(nrows=number_of_dimensions, ncols=1,
                                  figsize=(6, 4))
        fig.suptitle("Barcode Diagram")
        for dim, diagram in enumerate(dgms):
            births, deaths = [], []
            number_of_bars = len(diagram)
            if number_of_bars > 0:
                births = numpy.vstack([(element[0], i) for i, element in
                                       enumerate(diagram)])
                deaths = numpy.vstack([(element[1], i) for i, element in
                                       enumerate(diagram)])

            if number_of_dimensions == 1:
                ax.set_ylabel(labels[dim])
                ax.set_yticks([])
                for i, birth in enumerate(births):
                    ax.plot([birth[0], deaths[i][0]], [i * 0.1, i * 0.1],
                            color='#1f77b4')
            else:
                ax[dim].set_ylabel(labels[dim])
                ax[dim].set_yticks([])
                for i, birth in enumerate(births):
                    ax[dim].plot([birth[0], deaths[i][0]], [i * 0.1, i * 0.1],
                                 color='#1f77b4')

        # Accounting for the case of 'dgms' containing only data for the zeroth
        # homology group
        if dim == 0:
            ax.set_xlabel("$\epsilon$")
        else:
            ax[number_of_dimensions - 1].set_xlabel("$\epsilon$")
        fig.savefig(output + 'barcode_diagram.svg')


def obtain_filtration(persistence, dim, start_epsilon=0.0,
                      stop_epsilon=numpy.inf):
    """Calculate the epsilon values for a filtration complex.

    :param ripser.ripser persistence: The previously calculated persistence data
    :param int dim: The dimension of the persistent homology group for which to
    obtain a filtration of the simplicial complex
    :param float start_epsilon: The value to begin the calculation of epsilon
    values for sublevel complexes that define the filtration
    :param float stop_epsilon: A representation of positive infinity
    :returns: An array with 2-dimensional numpy.ndarray's, each consisting of
    two epsilon values: the first for the creation of that sublevel complex,
    whereas the second marks the epsilon value at which it is included
    into the next higher sublevel complex
    :rtype: numpy.ndarray
    """

    dgms = persistence['dgms']
    try:
        dgms[dim] in dgms
    except IndexError as ind_error:
        print(f'{ind_error}, there are no data for dimension {dim}!')
        return None

    filtered_diagram = numpy.vstack([simplex for simplex in dgms[dim]
                                     if start_epsilon <= simplex[1] <=
                                     stop_epsilon])
    return filtered_diagram


def obtain_connected_components(data_collection, persistence, epsilon):
    """Calculate the connected components for a specified value of epsilon.

    :param tuple data_collection: All data points and their respective
    identifiers used in the calculation of the persistence data
    :param ripser.ripser persistence: The previously calculated persistence data
    :param float epsilon: An epsilon at which to determine the connected
    components
    :returns: A tuple with two dicts, one with the data points for each
    connected component, the other with their respective identifiers
    :rtype: tuple(dict(int: list), dict(int: list))
    :raises Exception: if the number of data points and the elements of the
    connected components are not equal
    """

    data_points, identifiers = data_collection
    connected_data_points = collections.defaultdict(list)
    connected_identifiers = collections.defaultdict(list)
    distance_matrix = persistence['dperm2all']
    for element in numpy.nditer(distance_matrix, op_flags=['readwrite']):
        if element <= epsilon:
            element[...] = 1.0
        else:
            element[...] = 0.0
    _, labels = scipy.sparse.csgraph.connected_components(
        distance_matrix, directed=False, return_labels=True)
    if len(labels) == len(data_points):
        for i, entry in enumerate(labels):
            connected_data_points[entry].append(data_points[i])
            connected_identifiers[entry].append(identifiers[i])
    else:
        raise Exception('Number of data points and number of elements of all '
                        'connected components are not equal!')

    return connected_data_points, connected_identifiers


def write_connected_components_to_file(connected_components, output, epsilon):
    """Write all connected components to a file.

    :param dict connected_components: A dictionary with connected components
    :param str output: The directory to save the output to
    :param float epsilon: The epsilon used in :func:obtain_connected_components
    """

    with open(output + 'connected_components_epsilon_' + str(epsilon) + '.txt',
              'w') as file:
        for connected_component in connected_components:
            file.write('Cluster ' + str(connected_component) + ': ' + str(
                connected_components[connected_component]) + '\n')
