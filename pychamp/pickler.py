"""
.. module:: pyChampion.pickler
    :synopsis: Module to pickle and save settings

.. moduleauthor: Alex Nelson <w.alexnelson@gmail.com>

"""

import sys
import os
from django.conf import settings
import cPickle as pickle


def load():
    """Load settings"""
    file_path = os.path.join(settings.BASE_DIR, settings.PICKLE_FILE)

    try:
        data = pickle.load(open(file_path, "rb"))
    except EOFError:
        data = None

    return data


def pickle_data(data):
    """Save all data"""
    file_path = os.path.join(settings.BASE_DIR, settings.PICKLE_FILE)

    pickle.dump(data, open(file_path, "wb"))


def update_pickle_value(key, value):
    """Update provided key / value pair in pickle data"""
    data = load()

    if data is None:
        data = {key: value}
    else:
        data[key] = value

    pickle_data(data)