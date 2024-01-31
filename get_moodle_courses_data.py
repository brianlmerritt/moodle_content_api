import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

import os
from dotenv import load_dotenv
from lib.moodle_rest import moodle_rest
from lib.moodle_content_helpers import moodle_content_helpers

load_dotenv()
moodle_url = os.getenv('MOODLE_URL')
moodle_key = os.getenv('MOODLE_KEY')
idnumber_search = os.getenv('IDNUMBER_SEARCH')

moodle_rest_connection = moodle_rest(moodle_key, moodle_url)
moodle_content_helper = moodle_content_helpers(moodle_rest_connection)

courses = moodle_rest_connection.get_courses()


current_courses = moodle_rest_connection.get_matching_courses('idnumber', idnumber_search)

for _, current_course in current_courses.iterrows():
    moodle_content_helper.save_course_content(current_course['id'])


