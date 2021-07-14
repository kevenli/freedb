import unittest
from unittest import mock
from unittest.mock import MagicMock, Mock

from freedb.database import save_item


class DatabaseTest(unittest.TestCase):
    def test_save_item(self):
        mock_collection = Mock()
        mock_collection.insert_one = Mock(['doc'])
        
        doc = {'a': 1}
        ret = save_item(mock_collection, doc)
        self.assertIsNotNone(ret)

        mock_collection.insert_one.assert_called_once()
        saving_doc = mock_collection.insert_one.call_args[0][0]
        self.assertEqual(set(saving_doc.keys()), {'a', '_ts'})
