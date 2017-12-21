from django.conf import settings
from datetime import datetime
from decimal import Decimal
import requests
import os
import json


class ERSServer(object):
    """ Class for communications with the internal policy server"""
    def __init__(self):
        self.base_url = 'https://api.ersins.com/EDI/'

    def get_policy(self, state, policy_key):
        """ Get the policy information by its ID"""
        if settings.DEBUG:
            test_policy = os.path.join(
                settings.BASE_DIR, 'policy_filer', 'api', 'tests', 'fixtures',
                'policy info.json')
            with open(test_policy) as fp:
                return json.load(fp)
        else:
            response = requests.get(
                '{}/{}/{}'.format(self.base_url, state, policy_key)
            )
            response.raise_for_status()
            return response.json()


class Policy(object):

    def __init__(self, policy_info):
        self.policy_number = policy_info['general']['policy_number']
        self.bind_date = datetime.strptime(
            policy_info['general']['bind_date'], '%Y-%m-%d %H:%M:%S')
        self.expiration_date = datetime.strptime(
            policy_info['general']['expire_date'], '%Y-%m-%d %H:%M:%S')
        self.class_code = '00000'
        self.insured = PolicyInsured(policy_info['general']['client'])
        self.agent = PolicyAgent(policy_info['general']['agent'])

        self.policy_fee = Decimal("0.00")
        self.total_tax = Decimal("0.00")
        self.stamp_fee = Decimal("0.00")
        for fee in policy_info['general']['fees']:
            if fee['name'] == 'Brokerage Fee':
                self.policy_fee = Decimal(fee['value'].lstrip('$'))
            elif fee['name'] == 'Surplus Lines Tax':
                self.total_tax = Decimal(fee['value'].lstrip('$'))
            elif fee['name'] == 'Stamping Office Fee':
                self.stamp_fee = Decimal(fee['value'].lstrip('$'))

        self.total_gross = self.policy_fee + self.total_tax + self.stamp_fee


class PolicyInsured(object):

    def __init__(self, insured_info):
        self.name = insured_info['organization']
        self.address = PolicyAddress(insured_info['address'])
        self.phone = insured_info['phone']


class PolicyAgent(object):

    def __init__(self, insured_info):
        self.name = insured_info['name']
        self.company = insured_info['company']
        self.company_abbr = insured_info['companyabbr']
        self.address = PolicyAddress(insured_info['address'])
        self.phone = insured_info['phone']


class PolicyAddress(object):

    def __init__(self, address_info):
        self.street = address_info['street']
        self.city = address_info['city']
        self.state = address_info['state']
        self.zip = address_info['zip']
