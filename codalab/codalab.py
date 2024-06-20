import os
import re
import json
import requests
from bs4 import BeautifulSoup as bs
import xml.etree.ElementTree as ET


class CodaLab:
    def __init__(self, config):
        self.base_url = 'https://codalab.lisn.upsaclay.fr'
       
        self.login_url = f'{self.base_url}/accounts/login/'
        self.submit_url1 = f'{self.base_url}/s3direct/get_upload_params/'
        self.submit_url2 = f'{self.base_url}/competitions/{config["competition_id"]}#participate-submit_results'
        self.submit_url3 = f'{self.base_url}/api/competition/{config["competition_id"]}/submission'
        
        self.session = requests.Session()

        self.headers = {
            'X-Csrftoken': None
        }

        self.login(config['login'], config['password'])


    def login(self, username, password):
        res = self.session.get(self.login_url)
        soup = bs(res.text, 'html.parser')
        
        csrf_token = soup.find('input', attrs={'name': 'csrfmiddlewaretoken'})['value']
        
        login_data = {
            'csrfmiddlewaretoken': csrf_token,
            'login': username,
            'password': password,
        }

        self.session.post(self.login_url, data=login_data)
    
        res = self.session.get(self.base_url, data=login_data)
        soup = bs(res.text, 'html.parser')

        myinfo = soup.find('li', class_='dropdown')
        assert myinfo != None, "login fail"

        self.headers['X-Csrftoken'] = self.session.cookies['csrftoken']
        print('login success...')


    def s3direct(self, filename):
        data = {
            'type': 'application/zip',
            'name': filename,
            'dest': 'submissions'
        }

        res = self.session.post(self.submit_url1, data=data, headers=self.headers)
        res_data = json.loads(res.text)

        return res_data


    def py3_private(self, url):
        self.session.options(url)


    def submit(self, submit_dict):
        filename = os.path.basename(submit_dict['filename'])

        data = self.s3direct(filename)
        submit_url = data.pop('form_action')
        self.py3_private(submit_url)

        print('uploading file...')
        with open(submit_dict['filename'], 'rb') as f:
            files = {'file': (submit_dict['filename'], f)}
            res = self.session.post(submit_url, data=data, files=files)

        res4 = self.session.get(self.submit_url2)
        soup = bs(res4.text, 'html.parser')
        button = soup.find('button', id=re.compile(r'submissions_phase_\d+'))
        match = re.search(r'submissions_phase_(\d+)', button['id'])
        phase_id = match.group(1)

        root = ET.fromstring(res.content)
        locations = root.findall('.//Location')[0].text

        params = {
            'description': submit_dict['description'],
            'docker_image': '',
            'method_name': '',
            'method_description': '',
            'project_url': '',
            'publication_url': '',
            'team_name': '',
            'organization_or_affiliation': '',
            'bibtex': '',
            'phase_id': phase_id
        }

        data = {
            'id': locations,
            'name': '',
            'type': '',
            'size': ''
        }

        res = self.session.post(self.submit_url3, params=params, headers=self.headers, data=data)
        print(res)

        