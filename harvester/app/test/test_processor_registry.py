import os
import unittest

from app.processors.base import ProcessorRegistry

class ProcessorRegistryTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.processor_registry = ProcessorRegistry()
    
    def test_get_block_processors(self):
        processors = self.processor_registry.get_block_processors()
        self.assertTrue(processors)
        # for processor in processors:
        #     print(processor)
    
    def test_contracts_event_processors(self):
        processors = self.processor_registry.get_event_processors('contracts', 'CodeStored')
        self.assertTrue(processors)
        # for processor in processors:
        #     print(processor)

    
if __name__ == '__main__':
    unittest.main()
