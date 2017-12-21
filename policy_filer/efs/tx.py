from .base import BaseEFS
from policy_filer.api.utils import Policy
from django.conf import settings
from django.utils import timezone
from lxml import etree as ET
import requests


class TexasEFS(BaseEFS):
    NS_MAP = {
        'efs': 'http://www.slsot.org/efs',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    NAMESPACE = 'http://www.slsot.org/efs'
    SCHEMA_LOCATION = 'http://www.slsot.org/efs ' \
                      'http://efstest.slsot.org/efstest/xsd/SlsotEfsSchema2.xsd'

    def build_batch_request(self, b_requests):
        batch = []
        total_gross = 0
        for action, policy_info in b_requests:
            p_builder = getattr(self, 'build_%s' % action)
            batch.append(p_builder(policy_info))
            total_gross += policy_info.total_gross
        batch_attrib = {
            'AgLicNo': self.agent_lic,
            'BatchType': 'N',
            'ItemCnt': str(len(batch)),
            'TotalGross': str(total_gross)
        }

        root = self.E.Request
        root_attrib = {
            '{' + self.NS_MAP['xsi'] + '}schemaLocation': self.SCHEMA_LOCATION
        }
        batch_request = (
            root(
                self.E.EfsVersion('2.1'),
                self.E.Batch(*batch, **batch_attrib),
                **root_attrib
            )
        )
        return batch_request

    def build_new_policy(self, policy_info: Policy):

        new_policy = self.E.EFSPolicy(
            self.E.PolicyNumber(policy_info.policy_number),
            self.E.TransType('N'),
            self.E.Insured(policy_info.insured.name),
            self.E.ZipCode(policy_info.insured.address.zip),
            self.E.ClassCd(policy_info.class_code),
            self.E.PolicyFee(str(policy_info.policy_fee)),
            self.E.TotalTax(str(policy_info.total_tax)),
            self.E.TotalStampFee(str(policy_info.stamp_fee)),
            self.E.TotalGross(str(policy_info.total_gross)),
            self.E.EffectiveDate(policy_info.bind_date.strftime('%m/%d/%Y')),
            self.E.InceptionDate(policy_info.bind_date.strftime('%m/%d/%Y')),
            self.E.ExpirationDate(
                policy_info.expiration_date.strftime('%m/%d/%Y')),
            self.E.IssueDate(policy_info.bind_date.strftime('%m/%d/%Y')),
            self.E.WindStormExclusion('N'),
            self.E.FedCrUnion('N'),
            self.E.ECP('N'),
        )
        return new_policy

    def login_request(self, filename):
        l_params = {
            'requestType': 'L',
            'userID': self.user_id,
            'password': self.password,
            'fileName': filename,
        }
        response = requests.post(
            '%s/FileUpload' % self.base_url, params=l_params)
        response.raise_for_status()
        return response.cookies.get('session ID')

    def logout_request(self, session_id):
        l_params = {
            'requestType': 'O',
        }
        response = requests.post(
            '%s/FileUpload' % self.base_url,
            params=l_params,
            headers={'cookie': session_id}
        )
        response.raise_for_status()

    def submit_batch_request(self, batch_request):
        filename = 'Batch Request %s.xml' % timezone.now().isoformat()
        if settings.DEBUG:
            return '0000000'
        else:
            session_id = self.login_request(filename)
            upload_file = requests.post(
                '%s/FileUpload' % self.base_url,
                params={'requestType': 'M'},
                headers={'cookie': session_id},
                files={'file': (filename,
                                ET.tostring(batch_request, encoding='utf8'))
                       }
            )
            upload_file.raise_for_status()
            self.logout_request(session_id)
