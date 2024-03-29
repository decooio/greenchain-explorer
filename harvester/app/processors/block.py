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
#  block.py
#
import binascii
import dateutil
from sqlalchemy import distinct

from sqlalchemy.orm.exc import NoResultFound
from substrateinterface.utils.hasher import blake2_256

from app import settings, utils
from substrateinterface.utils.hasher import blake2_256

from app.models.data import Log, AccountAudit, Account, AccountIndexAudit, AccountIndex, \
    SessionValidator, IdentityAudit, IdentityJudgementAudit, IdentityJudgement, SearchIndex, AccountInfoSnapshot

from app.utils.ss58 import ss58_encode, ss58_encode_account_index, get_account_id_and_ss58_address
from scalecodec.base import ScaleBytes, RuntimeConfiguration

from app.processors.base import BlockProcessor
from scalecodec.types import LogDigest


class LogBlockProcessor(BlockProcessor):

    def accumulation_hook(self, db_session):
        log_digest_cls = self.substrate.runtime_config.get_decoder_class('sp_runtime::generic::digest::DigestItem')

        if log_digest_cls is None:
            raise NotImplementedError("No decoding class found for 'DigestItem'")

        self.block.count_log = len(self.block.logs)

        for idx, log_data in enumerate(self.block.logs):
            log_digest = log_digest_cls(data=ScaleBytes(log_data))
            log_digest.decode()

            log_type = log_digest.value_object[0]  # ('PreRuntime', GenericPreRuntime)
            # print(log_digest.value[log_type])
            log_inner_data = {}
            if ('PreRuntime' == log_type or 'Seal' == log_type) and self.substrate.implements_scaleinfo():
                engine_id = bytes.fromhex(log_digest.value[log_type][0][2:]).decode('utf-8')
                if engine_id == 'aura' and 'PreRuntime' == log_type:
                    predigest_data = log_digest.value['PreRuntime'][1]
                    try:
                        if predigest_data[:2] != '0x':
                            predigest_data = ScaleBytes(f"0x{predigest_data.encode().hex()}")
                        else:
                            predigest_data = ScaleBytes(predigest_data)
                    except ValueError:
                        predigest_data = ScaleBytes(f"0x{predigest_data.encode().hex()}")
                    aura_predigest = self.substrate.runtime_config.create_scale_object(
                        type_string='RawAuraPreDigest',
                        # data=ScaleBytes(log_digest.value['PreRuntime'][1])
                        data=predigest_data
                    )
                    aura_predigest.decode()
                    slot_number = aura_predigest.value['slot_number']
                    log_inner_data = {"data": {"slot_number": slot_number}, "engine": "aura"}
                elif engine_id == 'aura' and 'Seal' == log_type:
                    log_inner_data = {"data": log_digest.value['Seal'][1], "engine": "aura"}

                elif engine_id == 'BABE' and 'PreRuntime' == log_type:
                    predigest_data = log_digest.value['PreRuntime'][1]
                    try:
                        if predigest_data[:2] != '0x':
                            predigest_data = ScaleBytes(f"0x{predigest_data.encode().hex()}")
                        else:
                            predigest_data = ScaleBytes(predigest_data)
                    except ValueError:
                        predigest_data = ScaleBytes(f"0x{predigest_data.encode().hex()}")
                    babe_predigest = self.substrate.runtime_config.create_scale_object(
                        type_string='RawBabePreDigest',
                        # data=ScaleBytes(log_digest.value['PreRuntime'][1])
                        data=predigest_data
                    )
                    babe_predigest.decode()
                    rank_validator = babe_predigest[1].value['authority_index']
                    slot_number = babe_predigest[1].value['slot_number']
                    log_inner_data = {"data": {"slot_number": slot_number, "authority_index": rank_validator},
                                      "engine": "BABE"}
                elif engine_id == 'BABE' and 'Seal' == log_type:
                    log_inner_data = {"data": log_digest.value['Seal'][1], "engine": "BABE"}
            else:
                if type(log_digest.value) == str:
                    log_inner_data = log_digest.value
                else:
                    log_inner_data = log_digest.value[log_type]

            log = Log(
                block_id=self.block.id,
                log_idx=idx,
                type_id=log_digest.index,
                type=log_type,
                data=log_inner_data,
            )

            if log.type == 'PreRuntime':
                if log.data['engine'] == 'BABE':
                    # Determine block producer
                    self.block.authority_index = log.data['data']['authority_index']
                    self.block.slot_number = log.data['data']['slot_number']

                if log.data['engine'] == 'aura':
                    self.block.slot_number = log.data['data']['slot_number']

            log.save(db_session)

    def accumulation_revert(self, db_session):
        for item in Log.query(db_session).filter_by(block_id=self.block.id):
            db_session.delete(item)

        self.block.authority_index = None
        self.block.slot_number = None


class BlockTotalProcessor(BlockProcessor):

    def sequencing_hook(self, db_session, parent_block_data, parent_sequenced_block_data):

        if not parent_sequenced_block_data:
            parent_sequenced_block_data = {}

        if parent_block_data and parent_block_data['datetime']:
            self.sequenced_block.parent_datetime = parent_block_data['datetime']

            if type(parent_block_data['datetime']) is str:
                self.sequenced_block.blocktime = (self.block.datetime - dateutil.parser.parse(parent_block_data['datetime'])).total_seconds()
            else:
                self.sequenced_block.blocktime = (self.block.datetime - parent_block_data['datetime']).total_seconds()
        else:
            self.sequenced_block.blocktime = 0
            self.sequenced_block.parent_datetime = self.block.datetime

        self.sequenced_block.total_extrinsics = int(parent_sequenced_block_data.get('total_extrinsics', 0)) + self.block.count_extrinsics
        self.sequenced_block.total_extrinsics_success = int(parent_sequenced_block_data.get('total_extrinsics_success', 0)) + self.block.count_extrinsics_success
        self.sequenced_block.total_extrinsics_error = int(parent_sequenced_block_data.get('total_extrinsics_error', 0)) + self.block.count_extrinsics_error
        self.sequenced_block.total_extrinsics_signed = int(parent_sequenced_block_data.get('total_extrinsics_signed', 0)) + self.block.count_extrinsics_signed
        self.sequenced_block.total_extrinsics_unsigned = int(parent_sequenced_block_data.get('total_extrinsics_unsigned', 0)) + self.block.count_extrinsics_unsigned
        self.sequenced_block.total_extrinsics_signedby_address = int(parent_sequenced_block_data.get('total_extrinsics_signedby_address', 0)) + self.block.count_extrinsics_signedby_address
        self.sequenced_block.total_extrinsics_signedby_index = int(parent_sequenced_block_data.get('total_extrinsics_signedby_index', 0)) + self.block.count_extrinsics_signedby_index
        self.sequenced_block.total_events = int(parent_sequenced_block_data.get('total_events', 0)) + self.block.count_events
        self.sequenced_block.total_events_system = int(parent_sequenced_block_data.get('total_events_system', 0)) + self.block.count_events_system
        self.sequenced_block.total_events_module = int(parent_sequenced_block_data.get('total_events_module', 0)) + self.block.count_events_module
        self.sequenced_block.total_events_extrinsic = int(parent_sequenced_block_data.get('total_events_extrinsic', 0)) + self.block.count_events_extrinsic
        self.sequenced_block.total_events_finalization = int(parent_sequenced_block_data.get('total_events_finalization', 0)) + self.block.count_events_finalization
        self.sequenced_block.total_blocktime = int(parent_sequenced_block_data.get('total_blocktime', 0)) + self.sequenced_block.blocktime
        self.sequenced_block.total_accounts_new = int(parent_sequenced_block_data.get('total_accounts_new', 0)) + self.block.count_accounts_new

        self.sequenced_block.total_logs = int(parent_sequenced_block_data.get('total_logs', 0)) + self.block.count_log
        self.sequenced_block.total_accounts = int(parent_sequenced_block_data.get('total_accounts', 0)) + self.block.count_accounts
        self.sequenced_block.total_accounts_reaped = int(parent_sequenced_block_data.get('total_accounts_reaped', 0)) + self.block.count_accounts_reaped
        self.sequenced_block.total_sessions_new = int(parent_sequenced_block_data.get('total_sessions_new', 0)) + self.block.count_sessions_new
        self.sequenced_block.total_contracts_new = int(parent_sequenced_block_data.get('total_contracts_new', 0)) + self.block.count_contracts_new

        self.sequenced_block.session_id = int(parent_sequenced_block_data.get('session_id', 0))

        if parent_block_data and parent_block_data['count_sessions_new'] > 0:
            self.sequenced_block.session_id += 1

        if self.block.slot_number is not None:

            rank_validator = None

            if self.block.authority_index is not None:
                rank_validator = self.block.authority_index
            else:
                # In case of AURA, validator slot is determined by unique slot number
                validator_count = SessionValidator.query(db_session).filter_by(
                    session_id=self.sequenced_block.session_id
                ).count()

                if validator_count > 0:
                    rank_validator = int(self.block.slot_number) % validator_count

            # Retrieve block producer from session validator set
            validator = SessionValidator.query(db_session).filter_by(
                session_id=self.sequenced_block.session_id,
                rank_validator=rank_validator).first()

            if validator:
                self.sequenced_block.author = validator.validator_stash


class AccountBlockProcessor(BlockProcessor):

    def accumulation_hook(self, db_session):
        self.block.count_accounts_new += len(set(self.block._accounts_new))
        self.block.count_accounts_reaped += len(set(self.block._accounts_reaped))

        self.block.count_accounts = self.block.count_accounts_new - self.block.count_accounts_reaped

    def sequencing_hook(self, db_session, parent_block_data, parent_sequenced_block_data):

        for account_audit in AccountAudit.query(db_session).filter_by(block_id=self.block.id).order_by('event_idx'):
            try:
                account = Account.query(db_session).filter_by(id=account_audit.account_id).one()

                if account_audit.type_id == settings.ACCOUNT_AUDIT_TYPE_REAPED:
                    account.count_reaped += 1
                    account.is_reaped = True

                elif account_audit.type_id == settings.ACCOUNT_AUDIT_TYPE_NEW:
                    account.is_reaped = False

                    if account_audit.data and account_audit.data.get('is_tech_comm_member') is True:
                        account.is_tech_comm_member = True
                        account.was_tech_comm_member = True

                    if account_audit.data and account_audit.data.get('is_sudo') is True:
                        account.is_sudo = True
                        account.was_sudo = True

                    if account_audit.data and account_audit.data.get('is_treasury') is True:
                        account.is_treasury = True

                account.updated_at_block = self.block.id

            except NoResultFound:
                account = Account(
                    id=account_audit.account_id,
                    address=ss58_encode(account_audit.account_id, settings.SUBSTRATE_ADDRESS_TYPE),
                    hash_blake2b=blake2_256(binascii.unhexlify(account_audit.account_id)),
                    is_treasury=(account_audit.data or {}).get('is_treasury', False),
                    is_sudo=(account_audit.data or {}).get('is_sudo', False),
                    was_sudo=(account_audit.data or {}).get('is_sudo', False),
                    is_tech_comm_member=(account_audit.data or {}).get('is_tech_comm_member', False),
                    was_tech_comm_member=(account_audit.data or {}).get('is_tech_comm_member', False),
                    created_at_block=self.block.id,
                    updated_at_block=self.block.id
                )

                # Retrieve index in corresponding account
                account_index = AccountIndex.query(db_session).filter_by(account_id=account.id).first()

                if account_index:
                    account.index_address = account_index.short_address

                # Retrieve and set initial balance
                self.update_account_info(account)
                
                # # If reaped but does not exist, create new account for now
                # if account_audit.type_id != ACCOUNT_AUDIT_TYPE_NEW:
                #     account.is_reaped = True
                #     account.count_reaped = 1

            account.save(db_session)

        # Until SUDO and batch calls are processed separately we need to do a safety check to be sure we include all
        # accounts that have activity (lookup in account_index) in current block
        # TODO implement calls

        for search_index in db_session.query(SearchIndex.account_id).filter(
                SearchIndex.block_id == self.block.id,
                SearchIndex.account_id.notin_(db_session.query(Account.id))
        ).distinct():
            hex_account_id, ss58_address = get_account_id_and_ss58_address(search_index.account_id, settings.SUBSTRATE_ADDRESS_TYPE)
            account = Account(
                id=hex_account_id,
                address=ss58_encode(hex_account_id, settings.SUBSTRATE_ADDRESS_TYPE),
                hash_blake2b=blake2_256(binascii.unhexlify(hex_account_id)),
                created_at_block=self.block.id,
                updated_at_block=self.block.id
            )
            self.update_account_info(account)
            account.save(db_session)
    
    def update_account_info(self, account: Account):
        try:
            account_info_data_storage = utils.query_storage(pallet_name='System', storage_name='Account',
                                                            substrate=self.substrate,
                                                            params=['0x{}'.format(account.id)],
                                                            block_hash=self.block.hash)
            if account_info_data_storage:
                account_info_data = account_info_data_storage.value
                account.balance_free = account_info_data["data"]["free"]
                account.balance_reserved = account_info_data["data"]["reserved"]
                account.balance_total = account_info_data["data"]["free"] + account_info_data["data"]["reserved"]
                account.nonce = account_info_data["nonce"]
        except ValueError as e:
            print("ValueError: {}".format(e))
            pass
        except NotImplementedError as e:
            print("NotImplementedError: {}. Block: ${}".format(e, self.block.hash))
            raise


class AccountIndexBlockProcessor(BlockProcessor):

    def sequencing_hook(self, db_session, parent_block_data, parent_sequenced_block_data):

        for account_index_audit in AccountIndexAudit.query(db_session).filter_by(
                block_id=self.block.id
        ).order_by('event_idx'):

            if account_index_audit.type_id == settings.ACCOUNT_INDEX_AUDIT_TYPE_NEW:

                # Check if account index already exists
                account_index = AccountIndex.query(db_session).filter_by(
                    id=account_index_audit.account_index_id
                ).first()

                if not account_index:

                    account_index = AccountIndex(
                        id=account_index_audit.account_index_id,
                        created_at_block=self.block.id
                    )

                account_index.account_id = account_index_audit.account_id
                account_index.short_address = ss58_encode_account_index(
                    account_index_audit.account_index_id,
                    settings.SUBSTRATE_ADDRESS_TYPE
                )
                account_index.updated_at_block = self.block.id

                account_index.save(db_session)

                # Update index in corresponding account
                account = Account.query(db_session).get(account_index.account_id)

                if account:
                    account.index_address = account_index.short_address
                    account.save(db_session)

            elif account_index_audit.type_id == settings.ACCOUNT_INDEX_AUDIT_TYPE_REAPED:

                if account_index_audit.account_index_id:
                    account_index_list = AccountIndex.query(db_session).filter_by(
                        id=account_index_audit.account_index_id
                    )
                else:
                    account_index_list = AccountIndex.query(db_session).filter_by(
                        account_id=account_index_audit.account_id
                    )

                for account_index in account_index_list:

                    account_index.account_id = None
                    account_index.is_reclaimable = True
                    account_index.updated_at_block = self.block.id
                    account_index.save(db_session)


class IdentityBlockProcessor(BlockProcessor):

    def sequencing_hook(self, db_session, parent_block_data, parent_sequenced_block_data):

        for identity_audit in IdentityAudit.query(db_session).filter_by(block_id=self.block.id).order_by('event_idx'):

            account = Account.query(db_session).get(identity_audit.account_id)

            if account:

                if identity_audit.type_id == settings.IDENTITY_TYPE_SET:

                    account.has_identity = True

                    account.identity_display = identity_audit.data.get('display')
                    account.identity_email = identity_audit.data.get('email')
                    account.identity_legal = identity_audit.data.get('legal')
                    account.identity_riot = identity_audit.data.get('riot')
                    account.identity_web = identity_audit.data.get('web')
                    account.identity_twitter = identity_audit.data.get('twitter')

                    if account.has_subidentity:
                        # Update sub accounts
                        sub_accounts = Account.query(db_session).filter_by(parent_identity=account.id)
                        for sub_account in sub_accounts:
                            sub_account.identity_display = account.identity_display
                            sub_account.identity_email = account.identity_email
                            sub_account.identity_legal = account.identity_legal
                            sub_account.identity_riot = account.identity_riot
                            sub_account.identity_web = account.identity_web
                            sub_account.identity_twitter = account.identity_twitter

                            sub_account.save(db_session)

                    account.save(db_session)
                elif identity_audit.type_id in [settings.IDENTITY_TYPE_CLEARED, settings.IDENTITY_TYPE_KILLED]:

                    if account.has_subidentity:
                        # Clear sub accounts
                        sub_accounts = Account.query(db_session).filter_by(parent_identity=account.id)
                        for sub_account in sub_accounts:
                            sub_account.identity_display = None
                            sub_account.identity_email = None
                            sub_account.identity_legal = None
                            sub_account.identity_riot = None
                            sub_account.identity_web = None
                            sub_account.identity_twitter = None
                            sub_account.parent_identity = None
                            sub_account.has_identity = False

                            sub_account.identity_judgement_good = 0
                            sub_account.identity_judgement_bad = 0

                            sub_account.save(db_session)

                    account.has_identity = False
                    account.has_subidentity = False

                    account.identity_display = None
                    account.identity_email = None
                    account.identity_legal = None
                    account.identity_riot = None
                    account.identity_web = None
                    account.identity_twitter = None

                    account.identity_judgement_good = 0
                    account.identity_judgement_bad = 0

                    account.save(db_session)

                elif identity_audit.type_id == settings.IDENTITY_TYPE_SET_SUBS:

                    # Clear current subs
                    sub_accounts = Account.query(db_session).filter_by(parent_identity=account.id)
                    for sub_account in sub_accounts:
                        sub_account.identity_display = None
                        sub_account.identity_email = None
                        sub_account.identity_legal = None
                        sub_account.identity_riot = None
                        sub_account.identity_web = None
                        sub_account.identity_twitter = None
                        sub_account.parent_identity = None
                        sub_account.identity_judgement_good = 0
                        sub_account.identity_judgement_bad = 0
                        sub_account.has_identity = False

                        sub_account.save(db_session)

                    account.has_subidentity = False

                    # Process sub indenties
                    if len(identity_audit.data.get('subs', [])) > 0:

                        account.has_subidentity = True

                        for sub_identity in identity_audit.data.get('subs'):
                            sub_account = Account.query(db_session).get(sub_identity['account'].replace('0x', ''))
                            if sub_account:
                                sub_account.parent_identity = account.id
                                sub_account.subidentity_display = sub_identity['name']

                                sub_account.identity_display = account.identity_display
                                sub_account.identity_email = account.identity_email
                                sub_account.identity_legal = account.identity_legal
                                sub_account.identity_riot = account.identity_riot
                                sub_account.identity_web = account.identity_web
                                sub_account.identity_twitter = account.identity_twitter

                                sub_account.identity_judgement_good = account.identity_judgement_good
                                sub_account.identity_judgement_bad = account.identity_judgement_bad

                                sub_account.has_identity = True

                                sub_account.save(db_session)

                    account.save(db_session)


class IdentityJudgementBlockProcessor(BlockProcessor):

    def sequencing_hook(self, db_session, parent_block_data, parent_sequenced_block_data):

        for identity_audit in IdentityJudgementAudit.query(db_session).filter_by(block_id=self.block.id).order_by('event_idx'):

            if identity_audit.type_id == settings.IDENTITY_JUDGEMENT_TYPE_GIVEN:

                judgement = IdentityJudgement.query(db_session).filter_by(
                    account_id=identity_audit.account_id,
                    registrar_index=identity_audit.registrar_index
                ).first()

                if not judgement:

                    judgement = IdentityJudgement(
                        account_id=identity_audit.account_id,
                        registrar_index=identity_audit.registrar_index,
                        created_at_block=self.block.id
                    )

                if identity_audit.data:
                    judgement.judgement = identity_audit.data.get('judgement')
                    judgement.updated_at_block = self.block.id

                    judgement.save(db_session)

                    account = Account.query(db_session).get(identity_audit.account_id)

                    if account:

                        if judgement.judgement in ['Reasonable', 'KnownGood']:
                            account.identity_judgement_good += 1

                        if judgement.judgement in ['LowQuality', 'Erroneous']:
                            account.identity_judgement_bad += 1

                        account.save(db_session)

                        if account.has_subidentity:
                            # Update sub identities
                            sub_accounts = Account.query(db_session).filter_by(parent_identity=account.id)
                            for sub_account in sub_accounts:
                                sub_account.identity_judgement_good = account.identity_judgement_good
                                sub_account.identity_judgement_bad = account.identity_judgement_bad
                                sub_account.save(db_session)


class AccountInfoBlockProcessor(BlockProcessor):

    def accumulation_hook(self, db_session):
        # Store in AccountInfoSnapshot for all processed search indices and per 10000 blocks

        if self.block.id % settings.BALANCE_FULL_SNAPSHOT_INTERVAL == 0:
            from app.tasks import update_balances_in_block

            if settings.CELERY_RUNNING:
                update_balances_in_block.delay(self.block.id)
            else:
                update_balances_in_block(self.block.id)
        else:
            # Retrieve unique accounts in all searchindex records for current block
            for search_index in db_session.query(distinct(SearchIndex.account_id)).filter_by(block_id=self.block.id):
                self.harvester.create_balance_snapshot(
                    block_id=self.block.id,
                    block_hash=self.block.hash,
                    account_id=search_index[0]
                )

    def sequencing_hook(self, db_session, parent_block, parent_sequenced_block):
        # Update Account according to AccountInfoSnapshot

        for account_info in AccountInfoSnapshot.query(db_session).filter_by(block_id=self.block.id):
            account = Account.query(db_session).get(account_info.account_id)
            if account:
                account.balance_total = account_info.balance_total
                account.balance_reserved = account_info.balance_reserved
                account.balance_free = account_info.balance_free
                account.nonce = account_info.nonce
                account.save(db_session)


