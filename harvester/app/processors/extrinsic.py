#  Polkascan PRE Harvester
#
#  Copyright 2018-2020 openAware BV (NL).
#  This file is part of Polkascan.
#
#  Polkascan is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Polkascan is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Polkascan. If not, see <http://www.gnu.org/licenses/>.
#
#  extrinsic.py
#

import dateutil.parser
import pytz
import traceback
from app import settings
from app.models.data import IdentityAudit, Account, Contract, ContractInstance, ContractInstanceExtrinsic
from app.processors.base import ExtrinsicProcessor
from app.utils.ss58 import ss58_encode
from substrateinterface import ContractMetadata

class TimestampExtrinsicProcessor(ExtrinsicProcessor):

    module_id = 'timestamp'
    call_id = 'set'

    def accumulation_hook(self, db_session):

        if self.extrinsic.success:
            # Store block date time related fields
            for param in self.extrinsic.params:
                if param.get('name') == 'now':
                    self.block.set_datetime(dateutil.parser.parse(param.get('value')).replace(tzinfo=pytz.UTC))


class DemocracyVoteExtrinsicProcessor(ExtrinsicProcessor):

    module_id = 'democracy'
    call_id = 'vote'

    def process_search_index(self, db_session):

        if self.extrinsic.success:

            sorting_value = None

            # Try to retrieve balance of vote
            if self.extrinsic.params[1]['type'] == 'AccountVote<BalanceOf>':
                if 'Standard' in self.extrinsic.params[1]['value']:
                    sorting_value = self.extrinsic.params[1]['value']['Standard']['balance']

            search_index = self.add_search_index(
                index_type_id=settings.SEARCH_INDEX_DEMOCRACY_VOTE,
                account_id=self.extrinsic.address,
                sorting_value=sorting_value
            )

            search_index.save(db_session)


class DemocracyProxyVote(ExtrinsicProcessor):

    module_id = 'democracy'
    call_id = 'proxy_vote'

    def process_search_index(self, db_session):

        if self.extrinsic.success:

            search_index = self.add_search_index(
                index_type_id=settings.SEARCH_INDEX_DEMOCRACY_PROXY_VOTE,
                account_id=self.extrinsic.address
            )

            search_index.save(db_session)


class DemocracySecond(ExtrinsicProcessor):

    module_id = 'democracy'
    call_id = 'second'

    def process_search_index(self, db_session):

        if self.extrinsic.success:

            search_index = self.add_search_index(
                index_type_id=settings.SEARCH_INDEX_DEMOCRACY_SECOND,
                account_id=self.extrinsic.address
            )

            search_index.save(db_session)


class IndentitySetSubsExtrinsicProcessor(ExtrinsicProcessor):

    module_id = 'identity'
    call_id = 'set_subs'

    def process_search_index(self, db_session):

        if self.extrinsic.success:
            search_index = self.add_search_index(
                index_type_id=settings.SEARCH_INDEX_IDENTITY_SET_SUBS,
                account_id=self.extrinsic.address
            )

            search_index.save(db_session)


class StakingBond(ExtrinsicProcessor):

    module_id = 'staking'
    call_id = 'bond'

    def process_search_index(self, db_session):

        if self.extrinsic.success:
            search_index = self.add_search_index(
                index_type_id=settings.SEARCH_INDEX_STAKING_BONDED,
                account_id=self.extrinsic.address,
                sorting_value=self.extrinsic.params[1]['value']
            )

            search_index.save(db_session)


class StakingBondExtra(ExtrinsicProcessor):

    module_id = 'staking'
    call_id = 'bond_extra'

    def process_search_index(self, db_session):

        if self.extrinsic.success:
            search_index = self.add_search_index(
                index_type_id=settings.SEARCH_INDEX_STAKING_BONDED,
                account_id=self.extrinsic.address,
                sorting_value=self.extrinsic.params[0]['value']
            )

            search_index.save(db_session)


class StakingUnbond(ExtrinsicProcessor):

    module_id = 'staking'
    call_id = 'unbond'

    def process_search_index(self, db_session):

        if self.extrinsic.success:
            search_index = self.add_search_index(
                index_type_id=settings.SEARCH_INDEX_STAKING_UNBONDED,
                account_id=self.extrinsic.address,
                sorting_value=self.extrinsic.params[0]['value']
            )

            search_index.save(db_session)


class StakingWithdrawUnbonded(ExtrinsicProcessor):

    module_id = 'staking'
    call_id = 'withdraw_unbonded'

    def process_search_index(self, db_session):

        if self.extrinsic.success:
            search_index = self.add_search_index(
                index_type_id=settings.SEARCH_INDEX_STAKING_WITHDRAWN,
                account_id=self.extrinsic.address
            )

            search_index.save(db_session)


class StakingNominate(ExtrinsicProcessor):

    module_id = 'staking'
    call_id = 'nominate'

    def process_search_index(self, db_session):

        if self.extrinsic.success:
            search_index = self.add_search_index(
                index_type_id=settings.SEARCH_INDEX_STAKING_NOMINATE,
                account_id=self.extrinsic.address
            )

            search_index.save(db_session)


class StakingValidate(ExtrinsicProcessor):

    module_id = 'staking'
    call_id = 'validate'

    def process_search_index(self, db_session):

        if self.extrinsic.success:
            search_index = self.add_search_index(
                index_type_id=settings.SEARCH_INDEX_STAKING_VALIDATE,
                account_id=self.extrinsic.address
            )

            search_index.save(db_session)


class StakingChill(ExtrinsicProcessor):

    module_id = 'staking'
    call_id = 'chill'

    def process_search_index(self, db_session):

        if self.extrinsic.success:
            search_index = self.add_search_index(
                index_type_id=settings.SEARCH_INDEX_STAKING_CHILL,
                account_id=self.extrinsic.address
            )

            search_index.save(db_session)


class StakingSetPayee(ExtrinsicProcessor):

    module_id = 'staking'
    call_id = 'set_payee'

    def process_search_index(self, db_session):

        if self.extrinsic.success:
            search_index = self.add_search_index(
                index_type_id=settings.SEARCH_INDEX_STAKING_SET_PAYEE,
                account_id=self.extrinsic.address
            )

            search_index.save(db_session)


class ElectionsSubmitCandidacy(ExtrinsicProcessor):

    module_id = 'electionsphragmen'
    call_id = 'submit_candidacy'

    def process_search_index(self, db_session):

        if self.extrinsic.success:
            search_index = self.add_search_index(
                index_type_id=settings.SEARCH_INDEX_COUNCIL_CANDIDACY_SUBMIT,
                account_id=self.extrinsic.address
            )

            search_index.save(db_session)


class ElectionsVote(ExtrinsicProcessor):

    module_id = 'electionsphragmen'
    call_id = 'vote'

    def process_search_index(self, db_session):

        if self.extrinsic.success:
            search_index = self.add_search_index(
                index_type_id=settings.SEARCH_INDEX_COUNCIL_CANDIDACY_VOTE,
                account_id=self.extrinsic.address,
                sorting_value=self.extrinsic.params[1]['value']
            )

            search_index.save(db_session)

            # Reverse lookup
            for candidate in self.extrinsic.params[0]['value']:
                search_index = self.add_search_index(
                    index_type_id=settings.SEARCH_INDEX_COUNCIL_CANDIDACY_VOTE,
                    account_id=candidate.replace('0x', ''),
                    sorting_value=self.extrinsic.params[1]['value']
                )

                search_index.save(db_session)


class TreasuryProposeSpend(ExtrinsicProcessor):

    module_id = 'treasury'
    call_id = 'propose_spend'

    def process_search_index(self, db_session):

        if self.extrinsic.success:
            search_index = self.add_search_index(
                index_type_id=settings.SEARCH_INDEX_TREASURY_PROPOSED,
                account_id=self.extrinsic.address,
                sorting_value=self.extrinsic.params[0]['value']
            )

            search_index.save(db_session)

            # Add Beneficiary

            search_index = self.add_search_index(
                index_type_id=settings.SEARCH_INDEX_TREASURY_PROPOSED,
                account_id=self.extrinsic.params[1]['value'].replace('0x', ''),
                sorting_value=self.extrinsic.params[0]['value']
            )

            search_index.save(db_session)


class SudoSetKey(ExtrinsicProcessor):

    module_id = 'sudo'
    call_id = 'set_key'

    def sequencing_hook(self, db_session, parent_block, parent_sequenced_block):
        if self.extrinsic.success:

            sudo_key = self.extrinsic.params[0]['value'].replace('0x', '')

            Account.query(db_session).filter(
                Account.id == sudo_key, Account.was_sudo == False
            ).update({Account.was_sudo: True}, synchronize_session='fetch')

            Account.query(db_session).filter(
                Account.id != sudo_key, Account.is_sudo == True
            ).update({Account.is_sudo: False}, synchronize_session='fetch')

            Account.query(db_session).filter(
                Account.id == sudo_key, Account.is_sudo == False
            ).update({Account.is_sudo: True}, synchronize_session='fetch')


class ContractCallExtrinsicProcessor(ExtrinsicProcessor):

    module_id = 'contracts'
    call_id = 'call'

    def accumulation_hook(self, db_session):
        try:
            for param in self.extrinsic.params:
                if param.get('name') == 'dest':
                    contract_address = ss58_encode(param.get('value').replace('0x', ''))
                elif param.get('name') == 'data':
                    encoded_message = param.get('value')

            if encoded_message is None or len(encoded_message) <= 0:
                print('Extrinsic {}: missing data param'.format(self.extrinsic.extrinsic_hash))
                return

            if contract_address is None:
                print('Extrinsic {}: missing dest param'.format(self.extrinsic.extrinsic_hash))
                return

            contract = db_session.query(Contract).\
                join(ContractInstance, Contract.code_hash == ContractInstance.code_hash).\
                filter(ContractInstance.address == contract_address).\
                first()

            contract_abi = contract.abi if contract is not None else None

            if contract_abi is None or len(contract_abi) <= 0:
                print('Contract {}: missing abi'.format(contract_address))
                return

            contract_meta = ContractMetadata(contract_abi, self.substrate)
            decoded_message = contract_meta.decode_message_data(encoded_message)

            self.extrinsic.contract_message = decoded_message

            # create contract instance extrinsic
            if decoded_message:
                to_address = ''
                for item in decoded_message.get("args", []):
                    if item.get("name") == 'to':
                        to_address = ss58_encode(item.get("value").replace('0x', ''))
                if to_address:
                    self.extrinsic.to_address = to_address

                contract_instance_extrinsic_obj = ContractInstanceExtrinsic(
                    block_id=self.extrinsic.block_id,
                    extrinsic_idx=self.extrinsic.extrinsic_idx,
                    from_address=ss58_encode(self.extrinsic.address),
                    to_address=to_address,
                    contract_address=contract_address,
                    message_name=decoded_message.get("name"),
                    message_args=decoded_message
                )
                contract_instance_extrinsic_obj.save(db_session)
            self.extrinsic.save(db_session)

        except Exception:
            print('Failed to decode contracts call extrinsic params. {}'.format(self.extrinsic.params))
            traceback.print_exc()