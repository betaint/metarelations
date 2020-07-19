#!/usr/bin/python3

"""
:synopsis: Example program.
"""

# standard library imports
import mailbox
import configparser

# imports from modules in ./src
from src import mailanalysis
from src import features
from src import persistence


# Read user specified inputs from config file
config = configparser.ConfigParser()
config.read('mail.conf')
config.sections()
INPUT = config['directories']['input']
OUTPUT_DIR = config['directories']['output_dir']
THRESHOLD = config.getint('additional', 'threshold',
                          fallback='default_threshold')


# Parse input and create persistence and barcode diagrams
mail = mailbox.mbox(INPUT, create=False)
try:
    mails_per_sender, datetimes_per_sender = mailanalysis.parse_mails(mail,
                                                                      THRESHOLD)
except FileNotFoundError as fnf_error:
    print(fnf_error)
else:
    # Create a pandas.DataFrame with features
    df = features.aggregate_dataframe(mails_per_sender, datetimes_per_sender)

    # Apply minmax-scaling to the features
    scaled_df = features.feature_scaling(df)

    # Calculate the data for a persistence diagram and save the diagram
    data_collection, persistence_data = persistence.calculate_persistence(scaled_df)
    persistence.plot_persistence_diagram(persistence_data, OUTPUT_DIR)

    # Calculate and save a barcode diagram
    persistence.plot_barcode_diagram(persistence_data, OUTPUT_DIR)

    # Identify the connected components for a specified value of epsilon and
    # save them in a file
    _, connected_identifiers = persistence.obtain_connected_components(
        data_collection, persistence_data, epsilon=0.6)
    persistence.write_connected_components_to_file(connected_identifiers,
                                                   OUTPUT_DIR, epsilon=0.6)
