import lxml.builder as builder


class BaseEFS(object):
    NS_MAP = {
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    NAMESPACE = ''
    SCHEMA_LOCATION = ''

    def __init__(self, base_url, user_id, password, agent_lic):
        self.base_url = base_url
        self.user_id = user_id
        self.password = password
        self.agent_lic = agent_lic
        self.E = builder.ElementMaker(namespace=self.NAMESPACE,
                                      nsmap=self.NS_MAP)

    def build_batch_request(self, requests):
        pass

    @staticmethod
    def build_new_policy(policy_info):
        pass

    def submit_batch_request(self):
        pass
