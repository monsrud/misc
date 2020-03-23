import urllib.request
import requests
import ssl
import base64
import pytest
import json
from enum import Enum


"""  
This is a rest client I wrote to interact with a product API. 
Other command line scripts that I wrote which used this API were used by testers
who were not familiar with coding but could assemble basic shell scripts to
automate setup and cleanup tasks.
"""


class api:

    requests.urllib3.disable_warnings()

    def __init__(self, ip=None, username=None, password=None):
        self.configuration = configuration
        self.baseurl = "https://" + ip + "/api/v1"
        self.username = username
        self.password = password

    class MIGRATION_TYPE(Enum):
        NFS = 'NFS'
        BLOCK = 'BLOCK'
        CIFS = 'CIFS'
        SMB = 'SMB'
        REPLICATION = 'REPLICATION'

    def get_auth_token(self):
        url = self.baseurl + "/auth"
        response = requests.get(url,
                                auth=(self.username,
                                      self.password),
                                verify=False)
        bearer = 'Bearer ' + response.text
        return {'Authorization': bearer}

    def get_job(self, job_id):
        """ Get a specific job """
        jobs = self.get_jobs()
        for job in jobs['jobs']:
            if job['id'] == int(job_id):
                return job

    def get_jobs(self):
        """ Get all jobs """
        url = self.baseurl + "/datamovement/jobs"
        response = requests.get(url,
                                headers=self.get_auth_token(),
                                verify=False)

        if (response.status_code != 200):
            pytest.fail("Unexpected status geting projects : " +
                        str(response.status_code))
        pprint.pprint(response.json())
        pprint.pprint(response.content)
        return response.json()

    def delete_jobs(self):
        """ Delete all jobs """
        jobs = self.get_jobs()
        pprint.pprint(jobs)
        print("jobs = " + str(len(jobs)))

        for job in jobs['jobs']:

            self.delete_job(job['id'])

    def delete_job(self, job_id):
        """ Remove a specific project by job id"""
        url = self.baseurl + "/datamovement/jobs/" + str(job_id)
        response = requests.delete(url,
                                   headers=self.get_auth_token(),
                                   verify=False)
        if (response.status_code != 204):
            pytest.fail("Unexpected status code deleting project : " +
                        str(response.status_code))

    def set_source(self, export_path=None,
                   hostname=None, migration_type=None,
                   username=None, password=None, serialnum=None,
                   remoteverifier=None):
        """ Set a source for a migration """
        if type(migration_type) == self.MIGRATION_TYPE:
            migration_type = migration_type.value

        if migration_type == self.MIGRATION_TYPE.NFS.value:
            return {'export': '{}'.format(export_path),
                    'host': '{}'.format(hostname),
                    'type': '{}'.format(migration_type)}

        if migration_type == self.MIGRATION_TYPE.SMB.value:
            return {'share': '{}'.format(export_path),
                    'host': '{}'.format(hostname),
                    'username': '{}'.format(username),
                    'password': '{}'.format(password),
                    'type': '{}'.format(migration_type)}

        if migration_type == self.MIGRATION_TYPE.BLOCK.value:
            return {'type': '{}'.format(migration_type),
                    'serialnumber': '{}'.format(serialnum)}

        if migration_type == self.MIGRATION_TYPE.REPLICATION.value:
            return {'hostname': '{}'.format(hostname),
                    'remoteverifier': '{}'.format(remoteverifier),
                    'type': '{}'.format(migration_type)}

    def set_destination(self, export_path=None,
                        hostname=None, migration_type=None,
                        username=None, password=None, serialnum=None,
                        remoteverifier=None):
        """ Set a destination for a migration """

        if type(migration_type) == self.MIGRATION_TYPE:
            migration_type = migration_type.value

        if migration_type == self.MIGRATION_TYPE.NFS.value:
            return {'export': '{}'.format(export_path),
                    'host': '{}'.format(hostname),
                    'type': '{}'.format(migration_type)}

        if migration_type == self.MIGRATION_TYPE.SMB.value:
            return {'share': '{}'.format(export_path),
                    'host': '{}'.format(hostname),
                    'username': '{}'.format(username),
                    'password': '{}'.format(password),
                    'type': '{}'.format(migration_type)}

        if migration_type == self.MIGRATION_TYPE.BLOCK.value:
            return {'type': '{}'.format(migration_type),
                    'serialnumber': '{}'.format(serialnum)}

        if migration_type == self.MIGRATION_TYPE.REPLICATION.value:
            return {'hostname': '{}'.format(hostname),
                    'remoteverifier': '{}'.format(remoteverifier),
                    'type': '{}'.format(migration_type)}

    def create_job(self,
                   label=None,
                   projectid=None,
                   source=None, destination=None,
                   encrypt=False):
        """ Create a job job """
        url = self.baseurl + "/datamovement/jobs"
        response = requests.post(url,
                                 json={'label': label,
                                       'projectid': int(projectid),
                                       'source':  source,
                                       'destination': destination,
                                       'encrypt': encrypt},
                                 headers=self.get_auth_token(),
                                 verify=False)

        if (response.status_code != 200):
            pytest.fail("Unexpected status code adding job : " +
                        str(response.status_code) + " " + str(response.reason))
        return response.json()

    def update_job(self, job_id, label, source, destination, encrypt=True):
        """ Update a job """

        data = {
            "source": source,
            "destination": source,
            "encrypt": encrypt,
            "label": '"{}"'.format(label)
        }

        url = self.baseurl + "/datamovement/jobs/" + str(job_id)
        response = requests.get(url,
                                headers=self.get_auth_token(),
                                verify=False)
        headers = self.get_auth_token()
        headers.update({"If-Match": response.headers['ETag'].strip('"')})

        response = requests.put(url,
                                json=data,
                                headers=headers,
                                verify=False)

        if (response.status_code != 200):
            pytest.fail("Unexpected status code updating job : " +
                        str(response.status_code))

        json = response.json()

        # verify what was set
        if json['label'] != '"{}"'.format(label):
            pytest.fail("Job Name did not match expected value.")

        if json['source'] != source:
            pytest.fail("Source did not match expected value.")

        if json['destination'] != destination:
            pytest.fail("Destination did not match expected value.")

        if json['encrypt'] != encrypt:
            pytest.fail("Encrypt did not match expected value.")

        return json

    def start_job(self, job_id, verify_migration):
        """ Start a job """

        verify_str = ""
        if verify_migration:
            verify_str = '?verify=true'
        else:
            verify_str = '?verify=false'

        url = self.baseurl + "/datamovement/jobs/" + \
            str(job_id) + "/start" + verify_str
        response = requests.post(url,
                                 headers=self.get_auth_token(),
                                 verify=False)

        if (response.status_code != 202):
            pytest.fail("Unexpected status geting projects : " +
                        str(response.status_code))

    def stop_job(self, job_id):
        """ Stop a job """

        url = self.baseurl + "/datamovement/jobs/" + str(job_id) + "/stop"
        response = requests.post(url,
                                 headers=self.get_auth_token(),
                                 verify=False)

        if (response.status_code != 202):
            pytest.fail("Unexpected status geting projects : " +
                        str(response.status_code))

    def get_project(self, project_id):
        """ Get a specific project by id"""
        projects = self.get_projects()
        for project in projects['projects']:
            if project['id'] == int(project_id):
                return project

    def get_projects(self):
        """ get the projects """
        url = self.baseurl + "/datamovement/projects"
        response = requests.get(url,
                                headers=self.get_auth_token(),
                                verify=False)
        if (response.status_code != 200):
            pytest.fail("Unexpected status geting projects : " +
                        str(response.status_code))
        return response.json()

    def update_project(self, project_id,
                       project_name,
                       defaultmigjobrate=10,
                       jobrunlimit=10):
        """ Update a project """

        data = {
            "defaultmigjobrate": defaultmigjobrate,
            "jobrunlimit": jobrunlimit,
            "name": '"{}"'.format(project_name)
        }

        url = self.baseurl + "/datamovement/projects/" + str(project_id)
        response = requests.get(url,
                                headers=self.get_auth_token(),
                                verify=False)
        headers = self.get_auth_token()
        headers.update({"If-Match": response.headers['ETag'].strip('"')})

        response = requests.put(url,
                                json=data,
                                headers=headers,
                                verify=False)

        if (response.status_code != 200):
            pytest.fail("Unexpected status code updating project : " +
                        str(response.status_code))

        json = response.json()

        # verify what was set
        if json['name'] != '"{}"'.format(project_name):
            pytest.fail("Project Name did not match expected value.")

        if json['defaultmigjobrate'] != defaultmigjobrate:
            pytest.fail("Defaultmigjobrate Name did not match expected value.")

        if json['jobrunlimit'] != jobrunlimit:
            pytest.fail("Jobrunlimit Name did not match expected value.")

        return json

    def create_project(self, name, jobrunlimit=None, defaultmigjobrate=None):
        """ add a projects """
        # returns a dictionary
        url = self.baseurl + "/datamovement/projects"
        response = requests.post(url,
                                 json={
                                     'defaultmigjobrate':  defaultmigjobrate,
                                     'jobrunlimit': jobrunlimit,
                                     'name':   name
                                 },
                                 headers=self.get_auth_token(),
                                 verify=False)
        if (response.status_code != 200):
            pytest.fail("Unexpected status code adding project : " +
                        str(response.status_code) + " " + str(response.content))

        return response.json()

    def delete_projects(self):
        """ Delete all projects """
        projects = self.get_projects()

        for project in projects['projects']:
            self.delete_project(project['id'])

    def delete_project(self, project_id):
        """ Remove a specific project by project id"""

        url = self.baseurl + "/datamovement/projects/" + str(project_id)
        response = requests.delete(url,
                                   headers=self.get_auth_token(),
                                   verify=False)

        if (response.status_code != 204):
            pytest.fail("Unexpected status code deleting project : " +
                        str(response.status_code) + " " + str(response.content))
