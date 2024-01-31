import pandas as pd
#import htppx
import json
import csv
#import beautifulsoup4 as bs4

class moodle_content_helpers:
    def __init__(self, moodle_rest) -> None:
        self.data_store_path = 'course_data/'
        self.moodle_rest = moodle_rest
        
    def get_book_content(self, book_cmid):
        pass

    def get_block_content(self, course_blocks):
        pass

    def get_page_content(self, page_cmid):
        pass

    def get_forum_content(self, forum_cmid):
        pass

    def store_course_content(self, course_id):
        
        self.moodle_rest.set_course(course_id)
        course = self.moodle_rest.get_course(course_id)
        print(f"\n\nCurrent Course: {course['fullname']}")
        course_name = course['fullname']
        course_idnumber = course['idnumber']
        course_content = self.moodle_rest.current_course_sections
        course_modules = self.moodle_rest.current_course_modules
        course_blocks = self.moodle_rest.current_course_blocks
        # Todo store each course in a different directory
        self.save_item_raw(course, f"{self.data_store_path}{course_idnumber}_course")
        self.save_item_raw(course_modules, f"{self.data_store_path}{course_idnumber}_modules")
        self.save_item_raw(course_content, f"{self.data_store_path}{course_idnumber}_sections")
        self.save_item_raw(course_blocks, f"{self.data_store_path}{course_idnumber}_blocks")

    def save_item_raw(self, item_to_save, filename):
        if isinstance(item_to_save, pd.DataFrame) or isinstance(item_to_save, pd.Series):
            item_to_save.to_csv(f"{filename}.csv")
        elif isinstance(item_to_save, dict):
            with open(f"{filename}.json", "w") as file:
                json.dump(item_to_save, file)
        elif isinstance(item_to_save, list):
            with open(f"{filename}.csv", "w") as file:
                writer = csv.writer(file)
                writer.writerows(item_to_save)
        return