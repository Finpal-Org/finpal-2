import unittest
from unittest.mock import patch, MagicMock
import json
import os
import sys

# Add the current directory to the path so we can import the azure-doc-ai module
sys.path.append(os.path.dirname(__file__))

# Import the module to test
from azure_doc_ai import extracted_result

class TestAzureDocAI(unittest.TestCase):
    def test_extracted_result(self):
        # Sample Azure API response
        sample_response = {
            'analyzeResult': {
                'documents': [{
                    'docType': 'receipt.retail',
                    'fields': {
                        'MerchantName': {'content': 'Test Store', 'confidence': 0.95},
                        'Total': {'content': '42.99', 'confidence': 0.98},
                        'TransactionDate': {'content': '2023-05-15', 'confidence': 0.99},
                        'Items': {
                            'valueArray': [
                                {
                                    'valueObject': {
                                        'Description': {'content': 'Test Item 1'},
                                        'TotalPrice': {'content': '10.99'},
                                        'Quantity': {'content': '1'}
                                    }
                                },
                                {
                                    'valueObject': {
                                        'Description': {'content': 'Test Item 2'},
                                        'TotalPrice': {'content': '32.00'},
                                        'Quantity': {'content': '2'}
                                    }
                                }
                            ]
                        }
                    }
                }]
            }
        }
        
        # Simulate Firebase functionality
        with patch('firebase_admin.firestore.client') as firestore_client:
            # Set up a simulated database connection
            doc_ref = MagicMock()
            collection_ref = MagicMock()
            collection_ref.document.return_value = doc_ref
            firestore_client.return_value.collection.return_value = collection_ref
            
            # Call the function
            result = extracted_result(sample_response)
            
            # Basic assertions for key fields
            self.assertIn('total', result)
            self.assertEqual(result['total']['content'], '42.99')
            self.assertIn('vendor', result)
            self.assertEqual(result['vendor']['name']['content'], 'Test Store')
            self.assertIn('date', result)
            self.assertEqual(result['date']['content'], '2023-05-15')
            self.assertIn('line_items', result)
            self.assertEqual(len(result['line_items']), 2)

if __name__ == '__main__':
    unittest.main() 