import mock
import unittest
import json, logging
import mock
from pagerduty.handler import PagerdutyHandler

@mock.patch("pypd.EventV2.create")
@mock.patch("pagerduty.handler.PagerdutyHandler.grab_event")
@mock.patch("pagerduty.handler.PagerdutyHandler.grab_settings")
@mock.patch("sys.stdin")
class TestPagerdutyHandler(unittest.TestCase):
    def event_no_teams(self):
        event = {}
        event['client'] = {
            "name": "test_client",
            "address": "127.0.0.1",
            "keepalive": {
                "handler": "sensu_deregister",
                "thresholds": {
                    "critical": 604800,
                    "warning": 300
                }
            },
            "metrics": {
                "cpu": {
                    "crit": 100,
                    "warning": 90
                },
                "disk": {
                    "crit": 5,
                    "warning": 8
                },
                "memory": {
                    "crit": 100,
                    "warning": 90
                }
            },
            "pools": {},
            "services": {
                "octopus-deploy": {
                    "service": "OctopusDeploy Tentacle"
                }
            },
            "subscriptions": [
                "win-svc-metrics",
                "octopus-deploy-service",
                "host-checks",
                "host-metrics",
                "client:test_client"
            ],
            "version": "1.2.0",
            "timestamp": 1529508402
        }
        event['check'] = {
            "thresholds": {
                "warning": 300,
                "critical": 604800
            },
            "handler": "sensu_pagerduty",
            "name": "keepalive",
            "severity": "error",
            "links": [{"href": "https://sensu.io", "text": "RunBook"}],
            "output": "No keepalive sent from client for 1337 seconds (>=300)",
            "status": 1,
            "type": "standard",
            "history": [ "1", "1", "1" ],
        }
        event.update({
            "occurrences": 3,
            "action": "create",
        })
        return event

    def settings_teams(self):
        settings = {}
        settings['pagerduty'] = {'api_key': 'default_key', 'svc_email': 'test@example.com', 'team_1': {'api_key': 'team_1_key'}, 'dynamic_description_prefix_key': 'name'}
        return settings

    def settings_no_teams(self):
        settings = {}
        settings['pagerduty'] = { 'api_key': 'default_key', 'svc_email': 'test@example.com', 'dynamic_description_prefix_key': 'name' }
        return settings

    '''Test handle if handler config (settings) and event['client'] has pager_team'''
    def test_handle_pager_team_client_and_settings(self, mock_stdin, mock_grab_settings, mock_grab_event, mock_event_create):
        settings = self.settings_teams()
        event = self.event_no_teams()
        event['client']['pager_team'] = 'team_1'
        stdin = mock_stdin.read.return_value = json.dumps(event)
        mock_event = mock_grab_event.return_value = event
        mock_settings = mock_grab_settings.return_value = settings
        handler = PagerdutyHandler()
        payload = {}
        payload = {
            'routing_key': 'team_1_key',
            'event_action': 'trigger',
            'dedup_key': 'keepalive/test_client',
            'images': None,
            'links': [{"href": "https://sensu.io", "text": "RunBook"}],
            'payload': {
                'summary': '( test_client ) No keepalive sent from client for 1337 seconds (>=300)',
                'severity': 'error',
                'source': 'test_client',
                'class': None,
                'group': None,
                'component': None,
                'custom_details': 'No keepalive sent from client for 1337 seconds (>=300)'
             }}
        logging.debug("Event called with pypd.EventV2.create(data=" + json.dumps(payload))
        mock_event_create.assert_called_with(data=payload)

    '''Test handle if handler config (settings) and event['check'] has pager_team'''
    def test_handle_pager_team_check_and_settings(self, mock_stdin, mock_grab_settings, mock_grab_event, mock_event_create):
        settings = self.settings_teams()
        event = self.event_no_teams()
        event['check']['pager_team'] = 'team_1'
        stdin = mock_stdin.read.return_value = json.dumps(event)
        mock_event = mock_grab_event.return_value = event
        mock_settings = mock_grab_settings.return_value = settings
        handler = PagerdutyHandler()
        payload = {}
        payload = {
            'routing_key': 'team_1_key',
            'event_action': 'trigger',
            'dedup_key': 'keepalive/test_client',
            'images': None,
            'links': [{"href": "https://sensu.io", "text": "RunBook"}],
            'payload': {
                'summary': '( test_client ) No keepalive sent from client for 1337 seconds (>=300)',
                'severity': 'error',
                'source': 'test_client',
                'class': None,
                'group': None,
                'component': None,
                'custom_details': 'No keepalive sent from client for 1337 seconds (>=300)'
             }}
        logging.debug("Event called with pypd.EventV2.create(data=" + json.dumps(payload))
        mock_event_create.assert_called_with(data=payload)

    '''Test handle if handler config (settings) has pager_team but event does not'''
    def test_handle_pager_team_settings_not_event(self, mock_stdin, mock_grab_settings, mock_grab_event, mock_event_create):
        settings = self.settings_teams()
        event = self.event_no_teams()
        stdin = mock_stdin.read.return_value = json.dumps(event)
        mock_event = mock_grab_event.return_value = event
        mock_settings = mock_grab_settings.return_value = settings
        handler = PagerdutyHandler()
        payload = {}
        payload = {
            'routing_key': 'default_key',
            'event_action': 'trigger',
            'dedup_key': 'keepalive/test_client',
            'images': None,
            'links': [{"href": "https://sensu.io", "text": "RunBook"}],
            'payload': {
                'summary': '( test_client ) No keepalive sent from client for 1337 seconds (>=300)',
                'severity': 'error',
                'source': 'test_client',
                'class': None,
                'group': None,
                'component': None,
                'custom_details': 'No keepalive sent from client for 1337 seconds (>=300)'
             }}
        logging.debug("Event called with pypd.EventV2.create(data=" + json.dumps(payload))
        mock_event_create.assert_called_with(data=payload)

    '''Test handle if event['check'] has pager_team but handler config (settings) does not'''
    def test_handle_pager_team_check_not_settings(self, mock_stdin, mock_grab_settings, mock_grab_event, mock_event_create):
        settings = self.settings_no_teams()
        event = self.event_no_teams()
        event['check']['pager_team'] = 'team_1'
        stdin = mock_stdin.read.return_value = json.dumps(event)
        mock_event = mock_grab_event.return_value = event
        mock_settings = mock_grab_settings.return_value = settings
        handler = PagerdutyHandler()
        payload = {}
        payload = {
            'routing_key': 'default_key',
            'event_action': 'trigger',
            'dedup_key': 'keepalive/test_client',
            'images': None,
            'links': [{"href": "https://sensu.io", "text": "RunBook"}],
            'payload': {
                'summary': '( test_client ) No keepalive sent from client for 1337 seconds (>=300)',
                'severity': 'error',
                'source': 'test_client',
                'class': None,
                'group': None,
                'component': None,
                'custom_details': 'No keepalive sent from client for 1337 seconds (>=300)'
             }}
        logging.debug("Event called with pypd.EventV2.create(data=" + json.dumps(payload))
        mock_event_create.assert_called_with(data=payload)

    '''Test handle if neither handler config (settings) or event has pager_team'''
    def test_handle_pager_team_no_event_no_settings(self, mock_stdin, mock_grab_settings, mock_grab_event, mock_event_create):
        settings = self.settings_no_teams()
        event = self.event_no_teams()
        stdin = mock_stdin.read.return_value = json.dumps(event)
        mock_event = mock_grab_event.return_value = event
        mock_settings = mock_grab_settings.return_value = settings
        handler = PagerdutyHandler()
        payload = {}
        payload = {
            'routing_key': 'default_key',
            'event_action': 'trigger',
            'dedup_key': 'keepalive/test_client',
            'images': None,
            'links': [{"href": "https://sensu.io", "text": "RunBook"}],
            'payload': {
                'summary': '( test_client ) No keepalive sent from client for 1337 seconds (>=300)',
                'severity': 'error',
                'source': 'test_client',
                'class': None,
                'group': None,
                'component': None,
                'custom_details': 'No keepalive sent from client for 1337 seconds (>=300)'
             }}
        logging.debug("Event called with pypd.EventV2.create(data=" + json.dumps(payload))
        mock_event_create.assert_called_with(data=payload)

    '''Test handle if severity is not info, warning, critical, or error'''
    def test_handle_severity_assert_fail(self, mock_stdin, mock_grab_settings, mock_grab_event, mock_event_create):
        settings = self.settings_no_teams()
        event = self.event_no_teams()
        event['check']['severity'] = 'thingy'
        stdin = mock_stdin.read.return_value = json.dumps(event)
        mock_event = mock_grab_event.return_value = event
        mock_settings = mock_grab_settings.return_value = settings
        handler = PagerdutyHandler()
        payload = {}
        payload = {
            'routing_key': 'default_key',
            'event_action': 'trigger',
            'dedup_key': 'keepalive/test_client',
            'images': None,
            'links': [{"href": "https://sensu.io", "text": "RunBook"}],
            'payload': {
                'summary': '( test_client ) No keepalive sent from client for 1337 seconds (>=300)',
                'severity': 'error',
                'source': 'test_client',
                'class': None,
                'group': None,
                'component': None,
                'custom_details': 'No keepalive sent from client for 1337 seconds (>=300)'
             }}
        logging.debug("Event called with pypd.EventV2.create(data=" + json.dumps(payload))
        mock_event_create.assert_called_with(data=payload)

    '''Test handle if event['check']['severity'] is info'''
    def test_handle_severity_info(self, mock_stdin, mock_grab_settings, mock_grab_event, mock_event_create):
        settings = self.settings_no_teams()
        event = self.event_no_teams()
        event['check']['severity'] = 'info'
        stdin = mock_stdin.read.return_value = json.dumps(event)
        mock_event = mock_grab_event.return_value = event
        mock_settings = mock_grab_settings.return_value = settings
        handler = PagerdutyHandler()
        payload = {}
        payload = {
            'routing_key': 'default_key',
            'event_action': 'trigger',
            'dedup_key': 'keepalive/test_client',
            'images': None,
            'links': [{"href": "https://sensu.io", "text": "RunBook"}],
            'payload': {
                'summary': '( test_client ) No keepalive sent from client for 1337 seconds (>=300)',
                'severity': 'info',
                'source': 'test_client',
                'class': None,
                'group': None,
                'component': None,
                'custom_details': 'No keepalive sent from client for 1337 seconds (>=300)'
             }}
        logging.debug("Event called with pypd.EventV2.create(data=" + json.dumps(payload))
        mock_event_create.assert_called_with(data=payload)

    '''Test handle if event['check']['severity'] is warning'''
    def test_handle_severity_warning(self, mock_stdin, mock_grab_settings, mock_grab_event, mock_event_create):
        settings = self.settings_no_teams()
        event = self.event_no_teams()
        event['check']['severity'] = 'warning'
        stdin = mock_stdin.read.return_value = json.dumps(event)
        mock_event = mock_grab_event.return_value = event
        mock_settings = mock_grab_settings.return_value = settings
        handler = PagerdutyHandler()
        payload = {}
        payload = {
            'routing_key': 'default_key',
            'event_action': 'trigger',
            'dedup_key': 'keepalive/test_client',
            'images': None,
            'links': [{"href": "https://sensu.io", "text": "RunBook"}],
            'payload': {
                'summary': '( test_client ) No keepalive sent from client for 1337 seconds (>=300)',
                'severity': 'warning',
                'source': 'test_client',
                'class': None,
                'group': None,
                'component': None,
                'custom_details': 'No keepalive sent from client for 1337 seconds (>=300)'
             }}
        logging.debug("Event called with pypd.EventV2.create(data=" + json.dumps(payload))
        mock_event_create.assert_called_with(data=payload)

    '''Test handle if event['check']['severity'] is critical'''
    def test_handle_severity_critical(self, mock_stdin, mock_grab_settings, mock_grab_event, mock_event_create):
        settings = self.settings_no_teams()
        event = self.event_no_teams()
        event['check']['severity'] = 'critical'
        stdin = mock_stdin.read.return_value = json.dumps(event)
        mock_event = mock_grab_event.return_value = event
        mock_settings = mock_grab_settings.return_value = settings
        handler = PagerdutyHandler()
        payload = {}
        payload = {
            'routing_key': 'default_key',
            'event_action': 'trigger',
            'dedup_key': 'keepalive/test_client',
            'images': None,
            'links': [{"href": "https://sensu.io", "text": "RunBook"}],
            'payload': {
                'summary': '( test_client ) No keepalive sent from client for 1337 seconds (>=300)',
                'severity': 'critical',
                'source': 'test_client',
                'class': None,
                'group': None,
                'component': None,
                'custom_details': 'No keepalive sent from client for 1337 seconds (>=300)'
             }}
        logging.debug("Event called with pypd.EventV2.create(data=" + json.dumps(payload))
        mock_event_create.assert_called_with(data=payload)

    '''Test handle if event['check']['severity'] is error'''
    def test_handle_severity_error(self, mock_stdin, mock_grab_settings, mock_grab_event, mock_event_create):
        settings = self.settings_no_teams()
        event = self.event_no_teams()
        event['check']['severity'] = 'error'
        stdin = mock_stdin.read.return_value = json.dumps(event)
        mock_event = mock_grab_event.return_value = event
        mock_settings = mock_grab_settings.return_value = settings
        handler = PagerdutyHandler()
        payload = {}
        payload = {
            'routing_key': 'default_key',
            'event_action': 'trigger',
            'dedup_key': 'keepalive/test_client',
            'images': None,
            'links': [{"href": "https://sensu.io", "text": "RunBook"}],
            'payload': {
                'summary': '( test_client ) No keepalive sent from client for 1337 seconds (>=300)',
                'severity': 'error',
                'source': 'test_client',
                'class': None,
                'group': None,
                'component': None,
                'custom_details': 'No keepalive sent from client for 1337 seconds (>=300)'
             }}
        logging.debug("Event called with pypd.EventV2.create(data=" + json.dumps(payload))
        mock_event_create.assert_called_with(data=payload)

    '''Test handle if output is a dictionary'''
    def test_handle_output_dict_with_PD_context(self, mock_stdin, mock_grab_settings, mock_grab_event, mock_event_create):
        settings = self.settings_no_teams()
        event = self.event_no_teams()
        event['check']['output'] = {
            'Summary': 'No keepalive sent from client',
            'Details': 'No keepalive sent from client for 1337 seconds (>=300)',
            'Status': 'ping results: 100% packet loss'
        }
        event['check']['pagerduty_contexts'] = ['This is a pd context', 'This is another pd context']
        stdin = mock_stdin.read.return_value = json.dumps(event)
        mock_event = mock_grab_event.return_value = event
        mock_settings = mock_grab_settings.return_value = settings
        handler = PagerdutyHandler()
        payload = {}
        payload = {
            'routing_key': 'default_key',
            'event_action': 'trigger',
            'dedup_key': 'keepalive/test_client',
            'images': None,
            'links': [{"href": "https://sensu.io", "text": "RunBook"}],
            'payload': {
                'summary': '( test_client ) No keepalive sent from client',
                'severity': 'error',
                'source': 'test_client',
                'class': None,
                'group': None,
                'component': None,
                'custom_details': {
                                    'Status': 'ping results: 100% packet loss',
                                    'Contexts': ['This is a pd context', 'This is another pd context'],
                                    'Details': 'No keepalive sent from client for 1337 seconds (>=300)'
                                  }
             }}
        logging.debug("Event called with pypd.EventV2.create(data=" + json.dumps(payload))
        mock_event_create.assert_called_with(data=payload)

    def test_handle_output_dict_with_no_PD_context(self, mock_stdin, mock_grab_settings, mock_grab_event, mock_event_create):
        settings = self.settings_no_teams()
        event = self.event_no_teams()
        event['check']['output'] = {
            'summary': 'No keepalive sent from client',
            'details': 'No keepalive sent from client for 1337 seconds (>=300)',
            'status': 'ping results: 100% packet loss'
        }
        stdin = mock_stdin.read.return_value = json.dumps(event)
        mock_event = mock_grab_event.return_value = event
        mock_settings = mock_grab_settings.return_value = settings
        handler = PagerdutyHandler()
        payload = {}
        payload = {
            'routing_key': 'default_key',
            'event_action': 'trigger',
            'dedup_key': 'keepalive/test_client',
            'images': None,
            'links': [{"href": "https://sensu.io", "text": "RunBook"}],
            'payload': {
                'summary': '( test_client ) No keepalive sent from client',
                'severity': 'error',
                'source': 'test_client',
                'class': None,
                'group': None,
                'component': None,
                'custom_details': {
                                    'Status': 'ping results: 100% packet loss',
                                    'Details': 'No keepalive sent from client for 1337 seconds (>=300)'
                                  }
             }}
        logging.debug("Event called with pypd.EventV2.create(data=" + json.dumps(payload))
        mock_event_create.assert_called_with(data=payload)

    def test_handle_output_no_status_no_PD_context(self, mock_stdin, mock_grab_settings, mock_grab_event, mock_event_create):
        settings = self.settings_no_teams()
        event = self.event_no_teams()
        event['check']['output'] = {
            'summary': 'No keepalive sent from client',
            'details': 'No keepalive sent from client for 1337 seconds (>=300)'
        }
        stdin = mock_stdin.read.return_value = json.dumps(event)
        mock_event = mock_grab_event.return_value = event
        mock_settings = mock_grab_settings.return_value = settings
        handler = PagerdutyHandler()
        payload = {}
        payload = {
            'routing_key': 'default_key',
            'event_action': 'trigger',
            'dedup_key': 'keepalive/test_client',
            'images': None,
            'links': [{"href": "https://sensu.io", "text": "RunBook"}],
            'payload': {
                'summary': '( test_client ) No keepalive sent from client',
                'severity': 'error',
                'source': 'test_client',
                'class': None,
                'group': None,
                'component': None,
                'custom_details': 'No keepalive sent from client for 1337 seconds (>=300)'
             }}
        logging.debug("Event called with pypd.EventV2.create(data=" + json.dumps(payload))
        mock_event_create.assert_called_with(data=payload)

if __name__ == '__main__':
    unittest.main()
