import os
import unittest

from scalecodec.type_registry import load_type_registry_file
from scalecodec.base import ScaleBytes
from substrateinterface import SubstrateInterface

class TestHelperFunctions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        type_registry_file = os.path.join(os.path.dirname(__file__), 'fixtures', 'greenchain.json')
        custom_type_registry = load_type_registry_file(type_registry_file)
        cls.substrate = SubstrateInterface(
            url='wss://rpc.greenchain.cc',
            type_registry=custom_type_registry,
            type_registry_preset='default'
        )


    def test_decode_scale(self):
        self.assertEqual(self.substrate.decode_scale('Compact<u32>', '0x08'), 2)

    def test_encode_scale(self):
        self.assertEqual(self.substrate.encode_scale('Compact<u32>', 3), ScaleBytes('0x0c'))

    def test_create_scale_object(self):
        scale_obj = self.substrate.create_scale_object("Bytes")

        self.assertEqual(scale_obj.encode("Test"), ScaleBytes("0x1054657374"))
        self.assertEqual(scale_obj.decode(ScaleBytes("0x1054657374")), "Test")

    def test_get_metadata_call_function(self):
        call_function = self.substrate.get_metadata_call_function("Balances", "transfer")
        self.assertEqual("transfer", call_function.name)
        self.assertEqual('dest', call_function.args[0].name)
        self.assertEqual('value', call_function.args[1].name)

    def test_get_metadata_call_functions(self):
        call_functions = self.substrate.get_metadata_call_functions()
        self.assertGreater(len(call_functions), 0)

    def test_get_metadata_constants(self):
        constants = self.substrate.get_metadata_constants()
        self.assertGreater(len(constants), 0)

    def test_get_metadata_storage_functions(self):
        storages = self.substrate.get_metadata_storage_functions()
        self.assertGreater(len(storages), 0)

    def test_get_metadata_error(self):
        error = self.substrate.get_metadata_error("System", "InvalidSpecName")
        self.assertEqual("InvalidSpecName", error.name)
        self.assertIsNotNone(error.docs)

    def test_get_metadata_errors(self):
        errors = self.substrate.get_metadata_errors()
        self.assertGreater(len(errors), 0)

    def test_get_metadata_constant(self):
        constant = self.substrate.get_metadata_constant("System", "BlockHashCount")
        self.assertEqual("BlockHashCount", constant.name)
        self.assertEqual("scale_info::4", constant.type)
        self.assertEqual("0x60090000", f"0x{constant.constant_value.hex()}")

    def test_get_metadata_storage_function(self):
        storage = self.substrate.get_metadata_storage_function("System", "Account")
        self.assertEqual("Account", storage.name)
        self.assertEqual("scale_info::0", storage.get_params_type_string()[0])
        self.assertEqual("Blake2_128Concat", storage.type['Map']['hashers'][0])

    def test_get_metadata_event(self):
        event = self.substrate.get_metadata_event("Balances", "Transfer")
        self.assertEqual("Transfer", event.name)
        self.assertEqual('scale_info::0', event.args[0].type)
        self.assertEqual('scale_info::0', event.args[1].type)
        self.assertEqual('scale_info::6', event.args[2].type)

    def test_storage_function_param_info(self):
        storage_function = self.substrate.get_metadata_storage_function("System", "Account")
        info = storage_function.get_param_info()
        self.assertEqual(1, len(info))

    def test_create_scale_object(self):
        # No exception should be thrown
        self.substrate.create_scale_object('scale_info::0')


if __name__ == '__main__':
    unittest.main()
