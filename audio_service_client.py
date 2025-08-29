
from dataclasses import dataclass, field

import boto3
import requests
from boto3.session import Session
from requests_aws_sign import AWSV4Sign


@dataclass
class AudioServiceClient:
    audio_service_base_url = None
    log = None

    # Base audio-service URL
    url: str
    auth: AWSV4Sign = field(init=False)

    def __post_init__(self):

        credentials = boto3.session.Session().get_credentials()
        self.auth = AWSV4Sign(credentials, 'us-east-1', 'execute-api')


    def get_audio_metadata(self, checksum):

        url = f'{self.url}/v2/audio/{checksum}/metadata'

        response = requests.get(url, auth=self.auth)

        if response.status_code == 400:
            return None

        response.raise_for_status()

        return response.json()


    def get_cohort(self, content_id):

        url = f'{self.url}/v2/cohorts/{content_id}'

        response = requests.get(url, auth=self.auth)

        if response.status_code == 404:
            return None

        response.raise_for_status()

        return response.json()

    def post_cohort(self, content_id, cohort):

        url = f'{self.url}/v2/cohorts/{content_id}'

        response = requests.post(url, auth=self.auth, data=cohort)

        if response.status_code == 404:
            return None

        response.raise_for_status()

        return response.json()