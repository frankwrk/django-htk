# Python Standard Library Imports
import base64
import time

# Third Party / PIP Imports
import requests

# HTK Imports
from htk.lib.google.gmail.constants import GMAIL_RESOURCES
from htk.utils import refresh
from htk.utils.regex import Re

class GmailAPI(object):
    """Interface to Gmail API

    https://developers.google.com/gmail/api/v1/reference/
    """
    def __init__(self, user, email=None):
        self.user = user
        self.email = email

    def get_resource_url(self, resource_name, **kwargs):
        user_id = self.email if self.email else 'me'
        values = {
            'user_id' : user_id,
        }
        values.update(kwargs)
        url = GMAIL_RESOURCES[resource_name] % values
        return url

    def get_authorization_header(self):
        g_social_auth = self.user.profile.get_social_user('google-oauth2', self.email)
        header = None
        if g_social_auth:
            # refreshes token if necessary
            if g_social_auth.access_token_expired():
                from social_django.utils import load_strategy
                access_token = g_social_auth.get_access_token(load_strategy())
                g_social_auth = refresh(g_social_auth)
            header = '%(token_type)s %(access_token)s' % g_social_auth.extra_data
        return header

    def request_get(self, resource_name, headers=None, params=None, resource_args=None):
        if resource_args is None:
            resource_args = {}
        url = self.get_resource_url(resource_name, **resource_args)
        if headers is None:
            headers = {}
        if params is None:
            params = {}
        headers.update({
            'Authorization' : self.get_authorization_header(),
        })
        response = requests.get(url, headers=headers, params=params)
        return response

    ##
    # Users.drafts
    # https://developers.google.com/gmail/api/v1/reference/#Users.drafts

    ##
    # Users.history
    # https://developers.google.com/gmail/api/v1/reference/#Users.history

    ##
    # User.labels
    # https://developers.google.com/gmail/api/v1/reference/#Users.labels

    def labels_list(self):
        """https://developers.google.com/gmail/api/v1/reference/users/labels/list
        """
        resource_name = 'labels_list'
        response = self.request_get(resource_name)
        if response.status_code == 200:
            response_json = response.json()
            labels = response_json['labels']
            labels = sorted(labels, key=lambda label: label['name'])
        elif response.status_code == 401:
            # unauthorized
            labels = None
        else:
            labels = None
        return labels

    ##
    # Users.messages
    # https://developers.google.com/gmail/api/v1/reference/#Users.messages

    def messages_list(self, q=''):
        """https://developers.google.com/gmail/api/v1/reference/users/messages/list
        """
        resource_name = 'messages_list'
        params = {}
        if q:
            params['q'] = q
        response = self.request_get(resource_name, params=params)
        if response.status_code == 200:
            response_json = response.json()
            messages = response_json.get('messages', [])
        elif response.status_code in (400, 401,):
            # bad request, unauthorized
            messages = []
        else:
            messages = []
        return messages

    def message_get(self, message_id, params=None):
        """https://developers.google.com/gmail/api/v1/reference/users/messages/get
        """
        resource_name = 'message_get'
        if params is None:
            params = {}
        resource_args = {
            'message_id' : message_id,
        }
        response = self.request_get(resource_name, params=params, resource_args=resource_args)
        if response.status_code == 200:
            response_json = response.json()
            message = GmailMessage(response_json)
        elif response.status_code in (400, 401,):
            # bad request, unauthorized
            message = None
        else:
            message = None
        return message

    ##
    # Users.messages.attachments
    # https://developers.google.com/gmail/api/v1/reference/#Users.messages.attachments

    ##
    # Users.threads
    # https://developers.google.com/gmail/api/v1/reference/#Users.threads

    ##
    # Users.settings
    # https://developers.google.com/gmail/api/v1/reference/#Users.settings

    ##
    # Users.settings.forwardingAddresses
    # https://developers.google.com/gmail/api/v1/reference/#Users.settings.forwardingAddresses

    ##
    # Users
    # https://developers.google.com/gmail/api/v1/reference/#Users

    ##
    # Users.settings.filters
    # https://developers.google.com/gmail/api/v1/reference/#Users.settings.filters

    ##
    # Users.settings.sendAs
    # https://developers.google.com/gmail/api/v1/reference/#Users.settings.sendAs

class GmailMessage(object):
    def __init__(self, message_data):
        self.message_data = message_data

    def get_html(self):
        """Returns the HTML part of a message from the API

        https://developers.google.com/gmail/api/v1/reference/users/messages/get
        """
        html_part = None
        for part in self.message_data['payload']['parts']:
            if part['mimeType'] == 'text/html':
                html_part = part
                break

        if html_part:
            message_body_data = html_part['body']['data']
            message_html = base64.b64decode(message_body_data.replace('-', '+').replace('_', '/'))
        else:
            message_html = None

        return message_html

    @property
    def headers(self):
        headers = self.message_data.get('payload', {}).get('headers', [])
        return headers

    @property
    def sender(self):
        sender = None
        for header in self.headers:
            if header['name'] == 'From':
                sender = header['value']
                break
        return sender

    @property
    def sender_email(self):
        email = None
        sender = self.sender
        if sender:
            gre = Re()
            gre.match(r'(?:.*) <(.*)>', sender)
            if gre.last_match:
                email = gre.last_match.group(1)
            else:
                email = sender
        return email

    @property
    def subject(self):
        subject = None
        for header in self.headers:
            if header['name'] == 'Subject':
                subject = header['value']
                break
        return subject