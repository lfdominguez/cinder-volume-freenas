# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2016 iXsystems
"""
FREENAS api for iXsystems FREENAS system.

Contains classes required to issue REST based api calls to FREENAS system.
"""

#from cinder.openstack.common import jsonutils
from oslo_log import log as logging
import urllib2
import simplejson as json

LOG = logging.getLogger(__name__)


class FreeNASServer(object):
    """FreeNAS server connection logic."""

    FREENAS_API_VERSION = "v1"
    TRANSPORT_TYPE = 'http'
    STYLE_LOGIN_PASSWORD = 'basic_auth'

    # FREENAS Commands
    SELECT_COMMAND = 'select'
    CREATE_COMMAND = 'create'
    UPDATE_COMMAND = 'update'
    DELETE_COMMAND = 'delete'

    # FREENAS API query tables
    REST_API_VOLUME = "/storage/volume"
    REST_API_EXTENT = "/services/iscsi/extent"
    REST_API_TARGET = "/services/iscsi/target"
    REST_API_TARGET_TO_EXTENT = "/services/iscsi/targettoextent"
    REST_API_TARGET_GROUP = "/services/iscsi/targetgroup/"
    REST_API_SNAPSHOT = "/storage/snapshot"
    ZVOLS = "zvols"
    TARGET_ID = -1 #We assume invalid id to begin with
    STORAGE_TABLE = "/storage"
    CLONE = "clone"
    # Command response format
    COMMAND_RESPONSE = {'status': '%s',
                        'response': '%s'}

    # Command status
    STATUS_OK = 'ok'
    STATUS_ERROR = 'error'

    def __init__(self, host, port,
                 username=None, password=None,
                 api_version=FREENAS_API_VERSION,
                 transport_type=TRANSPORT_TYPE,
                 style=STYLE_LOGIN_PASSWORD):
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self.set_api_version(api_version)
        self.set_transport_type(transport_type)
        self.set_style(style)

    def get_host(self):
        return self._host

    def get_port(self):
        return self._port

    def get_username(self):
        return self._username

    def get_password(self):
        return self._password

    def get_transport_type(self):
        return self._protocol

    def set_host(self, host):
        self._host = host

    def set_port(self, port):
        try:
            int(port)
        except ValueError:
            raise ValueError("Port must be integer")

    def set_username(self, username):
        self._username = username

    def set_password(self, password):
        self._password = password

    def set_api_version(self, api_version):
        self._api_version = api_version

    def set_transport_type(self, transport_type):
        self._protocol = transport_type

    def set_style(self, style):
        """Set the authorization style for communicating with the server.
           Supports basic_auth for now.
        """
        if style.lower() not in (FreeNASServer.STYLE_LOGIN_PASSWORD):
            raise ValueError('Unsupported authentication style')
        self._auth_style = style.lower()

    def get_url(self):
        """Returns connection string built using _protocol, _host,
           _port and _api_version fields
        """
        return '%s://%s/api/%s' % (self._protocol,
                                      self._host,
                                      self._api_version)



    def _create_request(self, request_d, param_list):
        """Creates urllib2.Request object."""
        if not self._username or not self._password:
            raise ValueError("Invalid username/password combination")
        auth = ('%s:%s' % (self._username,
                           self._password)).encode('base64')[:-1]
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Basic %s' % (auth,)}
        url = self.get_url() + request_d
        LOG.debug('url : %s', url)
        LOG.debug('param list : %s', param_list)
        return urllib2.Request(url, param_list, headers)

    def _get_method(self, command_d):
        """Select http method based on FREENAS command."""
        if command_d == self.SELECT_COMMAND:
            return 'GET'
        elif command_d == self.CREATE_COMMAND:
            return 'POST'
        elif command_d == self.DELETE_COMMAND:
            return 'DELETE'
        elif command_d == self.UPDATE_COMMAND:
            return 'PUT'
        else:
            return None

    def _parse_result(self, command_d, response_d):
        """parses the response upon execution of FREENAS API. COMMAND_RESPONSE is
           the dictionary object with status and response fields.
           If error, set status to ERROR else set it to OK
        """
        response_str = response_d.read()
        status = None
        if command_d == self.SELECT_COMMAND:
            status = self.STATUS_OK
            response_obj = response_str
        elif (command_d == self.CREATE_COMMAND or
              command_d == self.DELETE_COMMAND or
              command_d == self.UPDATE_COMMAND):
            response_obj = response_str
            status = self.STATUS_OK
        else:
            status = self.STATUS_ERROR
            response_obj = None

        self.COMMAND_RESPONSE['status'] = status
        self.COMMAND_RESPONSE['response'] = response_obj
        return self.COMMAND_RESPONSE

    def _get_error_info(self, err):
        """Collects error response message."""
        self.COMMAND_RESPONSE['status'] = self.STATUS_ERROR
        if isinstance(err, urllib2.HTTPError):
            self.COMMAND_RESPONSE['response'] = '%d:%s' % (err.code, err.msg)
        elif isinstance(err, urllib2.URLError):
            self.COMMAND_RESPONSE['response'] = '%s:%s' % \
                                                (str(err.reason.errno),
                                                 err.reason.strerror)
        else:
            return None
        return self.COMMAND_RESPONSE

    def invoke_command(self, command_d, request_d, param_list):
        """Invokes api and returns response object."""
        LOG.debug('invoke_command')
        request = self._create_request(request_d, param_list)
        method = self._get_method(command_d)
        if not method:
            raise FreeNASApiError("Invalid FREENAS command")
        request.get_method = lambda: method
        try:
            response_d = urllib2.urlopen(request)
            response = self._parse_result(command_d, response_d)
            LOG.debug("invoke_command : response for request %s : %s", request_d, json.dumps(response))
        except urllib2.HTTPError as e:
            error_d = self._get_error_info(e)
            if error_d:
                return error_d
            else:
                raise FreeNASApiError(e.code, e.msg)
        except Exception as e:
            error_d = self._get_error_info(e)
            if error_d:
                return error_d
            else:
                raise FreeNASApiError('Unexpected error', e)
        return response


class FreeNASApiError(Exception):
    """Base exception class for FREENAS api errors."""

    def __init__(self, code='unknown', message='unknown'):
        self.code = code
        self.message = message

    def __str__(self, *args, **kwargs):
        return 'FREENAS api failed. Reason - %s:%s' % (self.code, self.message)
