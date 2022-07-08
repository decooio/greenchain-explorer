import os
import unittest

from scalecodec import ScaleBytes
from scalecodec.type_registry import load_type_registry_file, load_type_registry_preset
from substrateinterface import SubstrateInterface, ContractInstance, ContractEvent, Keypair
from test import settings

class EntropyCoinTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        greenchain_type_file=os.path.join(os.path.dirname(__file__), 'fixtures', 'greenchain_types.json')
        greenchain_type_registry = load_type_registry_file(greenchain_type_file)
        cls.substrate = SubstrateInterface(
            url=settings.GREENCHAIN_NODE_URL,
            ss58_format=42,
            type_registry_preset='substrate-node-template',
            type_registry=greenchain_type_registry
        )

    def setUp(self) -> None:
        self.contract = ContractInstance.create_from_address(
            contract_address=settings.GREENCHAIN_ENTROPY_CONTRACT_ADDRESS,
            metadata_file=os.path.join(os.path.dirname(__file__), 'fixtures', 'ent.json'),
            substrate=self.substrate
        )

    def test_metadata_parsed(self):
        self.assertNotEqual(self.contract.metadata.metadata_dict, {})

    def test_calling_entropy_methods(self):
        alice = Keypair.create_from_uri('//Alice')

        result = self.contract.read(alice, 'name')
        self.assertEqual('Entropy Coin', result.contract_result_data.value)

        result = self.contract.read(alice, 'symbol')
        self.assertEqual('ENT', result.contract_result_data.value)

        result = self.contract.read(alice, 'decimals')
        self.assertEqual(6, result.contract_result_data.value)

        result = self.contract.read(alice, 'total_supply')
        self.assertEqual(1000000000000, result.contract_result_data.value)

        # {'success': {'data': 999900000000, 'flags': 0, 'gas_consumed': 13954500000}}  
        result = self.contract.read(alice, 'balance_of', args={'owner': alice.public_key})
        self.assertIn('success', result.value)

    def test_decode_contract_transfer_event(self):
        contract_event_data = '0x0101d43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d018eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a4800e1f505000000000000000000000000'
        contract_event_obj = ContractEvent(
            data=ScaleBytes(contract_event_data),
            runtime_config=self.substrate.runtime_config,
            contract_metadata=self.contract.metadata
        )
        contract_event_obj.decode()
        # {'name': 'Transfer', 'docs': [' Event emitted when a token transfer occurs.'], 'args': [{'docs': [], 'indexed': True, 'name': 'from', 'type': {'displayName': ['Option'], 'type': 18}, 'value': '0xd43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d'}, {'docs': [], 'indexed': True, 'name': 'to', 'type': {'displayName': ['Option'], 'type': 18}, 'value': '0x8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48'}, {'docs': [], 'indexed': True, 'name': 'value', 'type': {'displayName': ['Balance'], 'type': 3}, 'value': 100000000}]}
        self.assertEqual('Transfer', contract_event_obj.value['name'])
        self.assertEqual('from', contract_event_obj.value['args'][0]['name'])
        self.assertEqual('0xd43593c715fdd31c61141abd04a99fd6822c8558854ccde39a5684e7a56da27d', contract_event_obj.value['args'][0]['value'])
        self.assertEqual('to', contract_event_obj.value['args'][1]['name'])
        self.assertEqual('0x8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48', contract_event_obj.value['args'][1]['value'])
        self.assertEqual('value', contract_event_obj.value['args'][2]['name'])
        self.assertEqual(100000000, contract_event_obj.value['args'][2]['value'])

    def test_decode_contract_params_event(self):
        # contract_event_data = b'\x00\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x002\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        contract_event_data = '\x00\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x002\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'.encode('utf-8')
        contract_event_obj = ContractEvent(
            data=ScaleBytes(contract_event_data),
            runtime_config=self.substrate.runtime_config,
            contract_metadata=self.contract.metadata
        )
        contract_event_obj.decode()
        # {'name': 'Params', 'docs': [' Event emitted when params are set.'], 'args': [{'docs': [], 'indexed': True, 'name': 'basis_points_rate', 'type': {'displayName': ['u128'], 'type': 3}, 'value': 20}, {'docs': [], 'indexed': True, 'name': 'maximum_fee', 'type': {'displayName': ['u128'], 'type': 3}, 'value': 50}]}
        self.assertEqual('Params', contract_event_obj.value['name'])
        self.assertEqual('basis_points_rate', contract_event_obj.value['args'][0]['name'])
        self.assertEqual(20, contract_event_obj.value['args'][0]['value'])
        self.assertEqual('maximum_fee', contract_event_obj.value['args'][1]['name'])
        self.assertEqual(50, contract_event_obj.value['args'][1]['value'])


    def test_decode_contract_message(self):
        encoded_message_data = '0x84a15da18eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48c09ee605000000000000000000000000'
        decoded_message = self.contract.metadata.decode_message_data(encoded_message_data)
        self.assertEqual('transfer', decoded_message['name'])
        self.assertEqual('to', decoded_message['args'][0]['name'])
        self.assertEqual('0x8eaf04151687736326c9fea17e25fc5287613693c912909cb226aa4794f26a48', decoded_message['args'][0]['value'])
        self.assertEqual('value', decoded_message['args'][1]['name'])
        self.assertEqual(99000000, decoded_message['args'][1]['value'])
        print(decoded_message)


    def test_decode_contract_message_with_bool(self):
        encoded_message_data = '0xd764177190b5ab205c6974c9ea841be688864633dc9ca8a357843eeacf2314649965fe2201'
        decoded_message = self.contract.metadata.decode_message_data(encoded_message_data)
        self.assertEqual('set_account_private', decoded_message['name'])
        self.assertEqual('account', decoded_message['args'][0]['name'])
        self.assertEqual('0x90b5ab205c6974c9ea841be688864633dc9ca8a357843eeacf2314649965fe22', decoded_message['args'][0]['value'])
        self.assertEqual('private', decoded_message['args'][1]['name'])
        self.assertEqual(True, decoded_message['args'][1]['value'])
        print(decoded_message)
