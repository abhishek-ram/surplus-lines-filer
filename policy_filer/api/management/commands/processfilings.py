from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
from policy_filer.api.models import Filing
from policy_filer.api.utils import ERSServer, Policy
from policy_filer import efs
from collections import defaultdict
from lxml import etree as ET
import logging

logger = logging.getLogger('sl-filer')


class Command(BaseCommand):
    help = 'Process all pending insurance filings'

    @transaction.atomic
    def handle(self, *args, **options):
        # Loop through all the pending filings in the system
        ers = ERSServer()
        filing_list = defaultdict(list)
        for filing in Filing.objects.filter(status='P'):
            logger.info('Getting policy information for '
                        '{} from the server'.format(filing.policy_key))
            policy_info = ers.get_policy(filing.state, filing.policy_key)

            # Initialize the EFS for this state
            state_str = filing.get_state_display().title().replace(' ', '')
            action_str = filing.get_action_display().lower().replace(' ', '_')
            filing_list[state_str].append((action_str, Policy(policy_info)))

        # Process the filings for each state
        for state, policies in filing_list.items():
            logger.info('Begin processing filings for {}.'.format(state))

            state_efs_cls = getattr(efs, '%sEFS' % state)
            state_efs = state_efs_cls(**settings.EFS_SERVERS[state])

            batch_request = state_efs.build_batch_request(policies)
            logger.info('Batch request built successfully')
            print(ET.tostring(batch_request, pretty_print=True).decode())
