import pandas as pd
import httpx
import json

class moodle_rest:
    def __init__(self, moodle_token, moodle_url):
        self.moodle_token = moodle_token
        self.moodle_url = moodle_url
        self.rest_endpoint = '/webservice/rest/server.php'
        self.moodle_courses = None
        self.current_course = None
        self.current_course_blocks = None
        self.current_course_modules = None
        self.current_course_sections = None
        self.headers = {"Accept": "application/json"}
        self.timeout = 60 # let's not be too hasty
        self.get_courses()

  
    def get_courses(self):
        if self.moodle_courses is None:
            response = self.get_moodle_rest_request('core_course_get_courses')
            self.moodle_courses = pd.DataFrame(response)
        return self.moodle_courses

        
    def get_course(self, course_id):
        try:
            course = self.moodle_courses.loc[self.moodle_courses['id'] == course_id]
            return course.iloc[0]
        except:
            return None
        
    # general "search course fields for value" and if field valid name and match found return course
    def get_course_by(self, field='id', value=None):
        try:
            course = self.moodle_courses.loc[self.moodle_courses[field] == value]
            return course.iloc[0]
        except:
            return None

    def set_course(self, course_id):
        self.current_course = course_id
        self.current_course_blocks = pd.DataFrame(self.get_moodle_rest_request('core_block_get_course_blocks', courseid=course_id)['blocks'])
        course_content = pd.DataFrame(self.get_moodle_rest_request('core_course_get_contents', courseid=course_id))
        
        # Create a new dataframe course_modules
        course_modules = pd.DataFrame()
        for _, course_section in course_content.iterrows():
            modules_to_add = pd.DataFrame(course_section['modules'])
            modules_to_add['section_id'] = course_section['id']
            course_modules = pd.concat([course_modules, modules_to_add], ignore_index=True)
        self.current_course_sections = course_content.drop(columns=['modules'])
        self.current_course_modules = course_modules
        self.current_course_blocks = self.get_block_content(course_id)
        return self.get_course(course_id)

    def get_matching_courses(self, field='id', value=None):
        if "*" in value:
            pattern = value.replace("*", ".*")
            try:
                courses = self.moodle_courses[self.moodle_courses[field].str.match(pattern, na=False)]
                return courses
            except:
                return None
        else:
            try:
                courses = self.moodle_courses.loc[self.moodle_courses[field] == value]
                return courses
            except:
                return None

    # Note calling this with new course_id will update the current course
    def get_course_modules(self, course_id):
        if course_id == self.current_course:
            return self.current_course_modules
        else:
            self.set_course(course_id)
            return self.current_course_modules
        
    # Note calling this with new course_id will update the current course
    def get_course_blocks(self, course_id):
        if course_id == self.current_course:
            return self.current_course_blocks
        else:
            self.set_course(course_id)
            return self.current_course_blocks

    def extract_block_configs(self, block, key):
        #if block['name']  == 'html':
        configs = block['configs']
        if configs is not None and isinstance(configs, (list, tuple, set)):
            for item in configs:
                if item.get('name') == key:
                    return item['value']
        return None



    def get_block_content(self, course_id):
        blocks = pd.DataFrame(self.get_moodle_rest_request('core_block_get_course_blocks', courseid=course_id)['blocks'])
        blocks['block_title'] = None
        blocks['block_text'] = None
        # Apply the function only to rows where 'type' is 'html'
        blocks['block_title'] = blocks.apply(lambda row: self.extract_block_configs(row, 'title'), axis=1)
        blocks['block_text'] = blocks.apply(lambda row: self.extract_block_configs(row, 'text'), axis=1)
        return blocks

    def flatten_api_parameters(self, in_args, prefix=''):
        # Check if the input is a dictionary
        if isinstance(in_args, dict):
            flattened_params = {}
            for key, item in in_args.items():
                # If the item is a list, add brackets to the key
                new_prefix = f"{prefix}[{key}]" if isinstance(item, list) else f"{prefix}{key}"
                for sub_key, value in self.flatten_api_parameters(item, new_prefix).items():
                    flattened_params[sub_key] = value
            return flattened_params

        # Check if the input is a list
        elif isinstance(in_args, list):
            return {f"{prefix}[{idx}]": value
                    for idx, item in enumerate(in_args)
                    for key, value in self.flatten_api_parameters(item, '').items()}

        # Base case: not a list or a dictionary
        else:
            if prefix:
                return {prefix: in_args}
            else:
                print(f"\nValue error: {in_args}")
                return {}

    # Call Moodle API - note does not throw exception on error
    def get_moodle_rest_request(self, moodle_function , **kwargs):
        parameters = dict(self.flatten_api_parameters(kwargs))
        parameters.update({"wstoken": self.moodle_token, 'moodlewsrestformat': 'json', "wsfunction": moodle_function})
        try:
            response = httpx.get(self.moodle_url + self.rest_endpoint, params=parameters, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200 :
                response_data = response.json()
                return response.json()
            else:
                print(f"Error calling Moodle API\n: {response}")
        except:
            raise(f"Exception calling Moodle API\n: {response}")
        return None
        