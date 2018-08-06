
import mock
import unittest
from pagerduty.handler import PagerdutyHandler

class TestPagerdutyHandler(unittest.TestCase):
    def mock_event_no_pd(self):
        event = { "client": { "name": "test_client", "address": "127.0.0.1", "keepalive": { "handler": "sensu_deregister", "thresholds": { "critical": 604800, "warning": 300 } }, "metrics": { "cpu": { "crit": 100, "warning": 90 }, "disk": { "crit": 5, "warning": 8 }, "memory": { "crit": 100, "warning": 90 } }, "pools": {}, "python_path": "c:\\salt\\bin\\python.exe", "services": { "octopus-deploy": { "service": "OctopusDeploy Tentacle" } }, "subscriptions": [ "win-svc-metrics", "octopus-deploy-service", "host-checks", "host-metrics", "client:test_client" ], "version": "1.2.0", "timestamp": 1529508402 }, "check": { "thresholds": { "warning": 300, "critical": 604800 }, "handler": "sensu_pagerduty", "name": "keepalive", "severity": "thingies", "links": [{"href": "https://sensu.io", "text": "RunBook"}], "issued": 1529525039, "executed": 1529525039, "output": "No keepalive sent from client for 1337 seconds (>=300)", "status": 1, "type": "standard", "history": [ "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1" ], "total_state_change": 0 }, "occurrences": 543, "occurrences_watermark": 543, "action": "create", "timestamp": 1529525040, "id": "b0179314-b9f8-4707-8812-3cae6fdcbd53", "last_state_change": 1529508729, "last_ok": 1529508729, "silenced": False, "silenced_by": [] }
        return event

    def mock_event_check_pd(self):
        event = { "client": { "name": "test_client", "address": "127.0.0.1", "keepalive": { "handler": "sensu_deregister", "thresholds": { "critical": 604800, "warning": 300 } }, "metrics": { "cpu": { "crit": 100, "warning": 90 }, "disk": { "crit": 5, "warning": 8 }, "memory": { "crit": 100, "warning": 90 } }, "pools": {}, "python_path": "c:\\salt\\bin\\python.exe", "services": { "octopus-deploy": { "service": "OctopusDeploy Tentacle" } }, "subscriptions": [ "win-svc-metrics", "octopus-deploy-service", "host-checks", "host-metrics", "client:test_client" ], "version": "1.2.0", "timestamp": 1529508402 }, "check": { "thresholds": { "warning": 300, "critical": 604800 }, "handler": "sensu_pagerduty", "name": "keepalive", "pager_team": "team_1", "severity": "thingies", "links": [{"href": "https://sensu.io", "text": "RunBook"}], "issued": 1529525039, "executed": 1529525039, "output": "No keepalive sent from client for 1337 seconds (>=300)", "status": 1, "type": "standard", "history": [ "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1" ], "total_state_change": 0 }, "occurrences": 543, "occurrences_watermark": 543, "action": "create", "timestamp": 1529525040, "id": "b0179314-b9f8-4707-8812-3cae6fdcbd53", "last_state_change": 1529508729, "last_ok": 1529508729, "silenced": False, "silenced_by": [] }
        return event

    def mock_event_client_pd(self):
        event = { "client": { "name": "test_client", "address": "127.0.0.1", "keepalive": { "handler": "sensu_deregister", "thresholds": { "critical": 604800, "warning": 300 } }, "metrics": { "cpu": { "crit": 100, "warning": 90 }, "disk": { "crit": 5, "warning": 8 }, "memory": { "crit": 100, "warning": 90 } }, "pools": {}, "python_path": "c:\\salt\\bin\\python.exe", "services": { "octopus-deploy": { "service": "OctopusDeploy Tentacle" } }, "pager_team": "team_1", "subscriptions": [ "win-svc-metrics", "octopus-deploy-service", "host-checks", "host-metrics", "client:test_client" ], "version": "1.2.0", "timestamp": 1529508402 }, "check": { "thresholds": { "warning": 300, "critical": 604800 }, "handler": "sensu_pagerduty", "name": "keepalive", "severity": "thingies", "links": [{"href": "https://sensu.io", "text": "RunBook"}], "issued": 1529525039, "executed": 1529525039, "output": "No keepalive sent from client for 1337 seconds (>=300)", "status": 1, "type": "standard", "history": [ "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1", "1" ], "total_state_change": 0 }, "occurrences": 543, "occurrences_watermark": 543, "action": "create", "timestamp": 1529525040, "id": "b0179314-b9f8-4707-8812-3cae6fdcbd53", "last_state_change": 1529508729, "last_ok": 1529508729, "silenced": False, "silenced_by": [] }
        return event

    def mock_settings_teams(self):
        settings = {"pagerduty": {"api_key": "default_key", "svc_email": "test@example.com", "team_1": {"api_key": "team_1_key"}, "dynamic_description_prefix_key": "name"}}
        return settings

    def mock_settings_no_teams(self):
        settings = {"pagerduty": {"api_key": "default_key", "svc_email": "test@example.com", "dynamic_description_prefix_key": "name"}}
        return settings

    def test_incident_key_teams_check_pd(self):
        settings = self.mock_settings_teams()
        event = self.mock_event_check_pd()
        handler = PagerdutyHandler()
        self.assertEqual(handler.incident_key(settings, event), 'keepalive/test_client')

    def test_api_key_teams_check_pd(self):
        settings = self.mock_settings_teams()
        event = self.mock_event_check_pd()
        handler = PagerdutyHandler()
        self.assertEqual(handler.api_key(settings, event), 'team_1_key')

    def test_api_key_no_teams_check_pd(self):
        settings = self.mock_settings_no_teams()
        event = self.mock_event_check_pd()
        handler = PagerdutyHandler()
        self.assertEqual(handler.api_key(settings, event), 'default_key')

    def test_incident_key_teams_client_pd(self):
        settings = self.mock_settings_teams()
        event = self.mock_event_client_pd()
        handler = PagerdutyHandler()
        self.assertEqual(handler.incident_key(settings, event), 'keepalive/test_client')

    def test_api_key_teams_client_pd(self):
        settings = self.mock_settings_teams()
        event = self.mock_event_client_pd()
        handler = PagerdutyHandler()
        self.assertEqual(handler.api_key(settings, event), 'team_1_key')

    def test_api_key_no_teams_client_pd(self):
        settings = self.mock_settings_no_teams()
        event = self.mock_event_client_pd()
        handler = PagerdutyHandler()
        self.assertEqual(handler.api_key(settings, event), 'default_key')

    def test_incident_key_teams_no_pd(self):
        settings = self.mock_settings_teams()
        event = self.mock_event_no_pd()
        handler = PagerdutyHandler()
        self.assertEqual(handler.incident_key(settings, event), 'keepalive/test_client')

    def test_api_key_teams_no_pd(self):
        settings = self.mock_settings_teams()
        event = self.mock_event_no_pd()
        handler = PagerdutyHandler()
        self.assertEqual(handler.api_key(settings, event), 'default_key')

    def test_api_key_no_teams_no_pd(self):
        settings = self.mock_settings_no_teams()
        event = self.mock_event_no_pd()
        handler = PagerdutyHandler()
        self.assertEqual(handler.api_key(settings, event), 'default_key')

if __name__ == '__main__':
    unittest.main()