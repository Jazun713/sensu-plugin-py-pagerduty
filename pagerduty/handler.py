#/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Released under the same terms as Sensu (the MIT license); see LICENSE
# for details.

from __future__ import print_function
from sensu_plugin import SensuHandler
import sensu_plugin.utils as sensu_settings
import json, sys
import pypd
import argparse
import logging


class PagerdutyHandler(SensuHandler):
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument(
            '-j',
            '--json_config',
            required = False,
            default = 'pagerduty',
            help = 'The handler config key, i.e. pagerduty, in your JSON config'
        )
        self.parser.add_argument(
            '-a',
            '--api_key',
            required = False,
            default = '/etc/sensu/bin/sensu-plugin-py-pagerduty/pagerduty/api.key',
            help = 'The path where the PagerDuty API key file is stored'
        )
        (self.options, self.remain) = self.parser.parse_known_args()
        self.config = vars(self.options)["json_config"]
        key_path = vars(self.options)["api_key"]
        pypd.set_api_key_from_file(key_path)
        super(PagerdutyHandler, self).__init__()
        #settings = self.settings 
        #event = self.event

    def incident_key(self, settings=None, event=None):
        if not settings:
            settings = self.settings
        if not event:
            event = self.event
        try:
            source = event['check']['source']
            incident_id = '/'.join([source, event['check']['name'], event['client']['name']])
        except KeyError:
            incident_id = '/'.join([event['check']['name'], event['client']['name']])

        # Pretty sure this is broken, it's definitely not tested. Not sure what this was for in the Ruby implementation.
        try:
            dedup_rules = settings[self.config]['dedup_rules']
        except KeyError:
            dedup_rules = {}
        for key, val in dedup_rules:
            incident_id = incident_id.gsub(Regexp.new(key), val)
        return incident_id

    def api_key(self, settings=None, event=None):
        if not settings:
            settings = self.settings
        if not event:
            event = self.event
        try:
            api_key = settings[self.config]['api_key']
        except KeyError:
            sys.exit('Default integration key not found in config JSON')

        if 'pager_team' in event['check'] and event['check']['pager_team'] is not None:
            pager_team = event['check']['pager_team']
            try:
                logging.info("HANDLER: Your check config has a pager team of %s, using this key.", pager_team)
                api_key = settings[self.config][pager_team]['api_key']
            except KeyError:
                logging.warning("HANDLER: your check config has a pager team of %s but the team was not found in the handler config, using default key.", pager_team)
                api_key = settings[self.config]['api_key']
        elif 'pager_team' in event['client'] and event['client']['pager_team'] is not None:
            pager_team = event['client']['pager_team']
            try:
                logging.info("HANDLER: Your client config has a pager team of %s, using this key.", pager_team)
                api_key = settings[self.config][pager_team]['api_key']
            except KeyError:
                logging.warning("HANDLER: your client config has a pager team of %s but the team was not found in the handler config, using default key.", pager_team)
                api_key = settings[self.config]['api_key']
        else:
            logging.info("HANDLER: No client or check config for pager team, using default key.")
            api_key = settings[self.config]['api_key']
        return api_key

    def proxy_settings(self, settings=None, event=None):
        if not settings:
            settings = self.settings
        if not event:
            event = self.event
        proxy_settings = {}

        try:
            proxy_settings['proxy_host'] = settings[self.config]['proxy_host']
        except KeyError:
            proxy_settings['proxy_host'] = None
        try:
            proxy_settings['proxy_port'] = settings[self.config]['proxy_port']
        except KeyError:
            proxy_settings['proxy_port'] = 3128
        try:
            proxy_settings['proxy_username'] = settings[self.config]['proxy_username']
        except KeyError:
            proxy_settings['proxy_username'] = ''
        try:
            proxy_settings['proxy_password'] = settings[self.config]['proxy_password']
        except KeyError:
            proxy_settings['proxy_password'] = ''
        return proxy_settings

    def contexts(self, settings=None, event=None):
        if not settings:
            settings = self.settings
        if not event:
            event = self.event
        try:
            contexts = event['check']['pagerduty_contexts']
        except KeyError:
            contexts = None
        return contexts

    def description_prefix(self, settings=None, event=None):
    # dyanamic_description_prefix_key is attempting to match a key from the client config which is passed into the event data.
    # If this key doesn't exist we try to set it to the static prefix defined in the server side config (i.e. conf.d/pagerduty.json) --
    # using the key 'description_prefix'.  This can be any static value you want to have in front of the event summary in pagerduty.

        if not settings:
            settings = self.settings
        if not event:
            event = self.event
        try:
            description_prefix = event['client'][settings[self.config]['dynamic_description_prefix_key']]
        except KeyError:
            try:
                description_prefix = settings[self.config]['description_prefix']
            except KeyError:
                description_prefix = None
        return description_prefix

    def handle(self, settings=None, event=None):
        if not settings:
            settings = self.settings
        if not event:
            event = self.event
        print(event['action'])
        if settings[self.config] == None:
            sys.exit('HANDLER: invalid config: {settings[self.config] !r} you need to pass a key and not a file')
        incident_key = self.incident_key()
        description_prefix = self.description_prefix()
        proxy_settings = self.proxy_settings()
        try:
            incident_key_prefix = settings[self.config]['incident_key_prefix']
            incident_key = '/'.join([incident_key_prefix, incident_key()])
        except KeyError:
            pass

        # This needs testing
        if proxy_settings['proxy_host']:
            http_proxy_addr = ":".join(proxy_settings['proxy_host'], proxy_settings['proxy_port'])
            pypd.proxies = {
                'http': http_proxy_addr
            }
        else:
          if event['action'] == 'create' or event['action'] == 'flapping':
              try:
                  severity = event['check']['severity']
              except KeyError:
                  severity = 'error'
              try:
                  images = event['check']['images']
              except KeyError:
                  images = None
              try:
                  links = event['check']['links']
              except KeyError:
                  links = None
              event_summary = " ".join([description_prefix, event['check']['output']])
              try:
                  assert( severity in ['critical', 'error', 'warning', 'info'] )
              except AssertionError:
                  print('HANDLER: Severity must be "critical", "error", "warning", or "info"... \nSetting severity to "error".', file=sys.stderr)
                  severity = 'error'
              try:
                  pdclass = event['check']['class']
              except KeyError:
                  pdclass = None
              try:
                  group = event['check']['group']
              except KeyError:
                  group = None
              try:
                  component = event['check']['component']
              except KeyError:
                  component = None

              pypd.EventV2.create(data={
                  'routing_key': self.api_key(),
                  'event_action': 'trigger',
                  'dedup_key': incident_key,
                  'images': images,
                  'links': links,
                  'payload': {
                      'summary': event_summary,
                      'severity': severity,
                      'source': event['client']['name'],
                      'class': pdclass,
                      'group': group,
                      'component': component,
                      'custom_details': self.contexts()
                  }
              })

          elif event['action'] == 'resolve':
              try:
                  svc_email = settings[self.config]['svc_email']
              except KeyError:
                  sys.exit('HANDLER: A service email (svc_email) must be set in the handler config JSON on your server.\nHANDLER: Resolve not sent!')
              incidents = pypd.Incident.find(incident_key=incident_key, statuses=['triggered', 'acknowledged'])
              for incident in incidents:
                  incident.resolve(from_email=svc_email, resolution='Resolved via the API')

if __name__ == '__main__':
    f = PagerdutyHandler()
