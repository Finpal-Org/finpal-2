# import libraries
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
# ENV 
from dotenv import load_dotenv
# import firestore
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

load_dotenv() # access env

cred = credentials.Certificate(os.getenv("FIREBASE_KEY_PATH")) # private credentials
firebase_admin.initialize_app(cred) # init app with our project cred
db = firestore.client() # connect to db

# Azure Document Intelligence setup
endpoint = os.getenv("AZURE_ENDPOINT")
key = os.getenv("AZURE_KEY")

def analyze_receipt():
    # Path to the receipt file - make sure this is the correct path and a < 4mb size  
    receipt_path = "../assets/contoso-receipt.png"
        
    # Open the receipt img in binary mode (required by azure)
    with open(receipt_path, "rb") as f: # rb: read binary
        # Read the file content
        receipt_data = f.read()
        
        print(f"File size: {len(receipt_data) / (1024 * 1024):.2f} MB")
                
        print("\nAnalyzing receipt using Document Intelligence SDK...")
        try:
            # Create the Document Intelligence client
            document_intelligence_client = DocumentIntelligenceClient(
                endpoint=endpoint, 
                credential=AzureKeyCredential(key)
            )
            
            # Simply pass the binary data directly to begin_analyze_document
            # Let the SDK handle the details
            poller = document_intelligence_client.begin_analyze_document(
                "prebuilt-receipt", # Model ID for receipts
                body=receipt_data
            )
            
            # Wait for the result
            receipts = poller.result()
            
            # Process and store results
            extracted = {}
            
            # Check if we have documents in the result
            if receipts.documents:
                # Get the first receipt
                receipt = receipts.documents[0]
                print(f"Found receipt: {receipt.doc_type}")
                
                # Get all fields
                fields = receipt.fields
                
                # Store DocType information
                if receipt.doc_type:
                    extracted["DocType"] = receipt.doc_type
                
                # Process each field in the receipt
                # Using the field names from Document Intelligence Studio
                field_names = [
                    "CountryRegion", 
                    "MerchantAddress", 
                    "MerchantName",
                    "ReceiptType",
                    "Subtotal",
                    "TaxDetails",
                    "Total",
                    "TotalTax",
                    "TransactionDate",
                    "TransactionTime",
                    # Add any other fields you saw in the Document Intelligence Studio
                    "MerchantPhoneNumber",
                    "Tip",
                    "PaymentType",
                    "Currency",
                    "TransactionId"
                ]
                
                # Extract fields
                for field_name in field_names:
                    if field_name in fields:
                        field = fields[field_name]
                        
                        # Extract basic field data
                        field_data = {
                            "content": field.get("content"),
                            "confidence": field.get("confidence")
                        }
                        
                        # Special handling for TaxDetails which has a nested structure
                        # This is based on the Document Intelligence Studio output
                        if field_name == "TaxDetails" and field.get("valueObject"):
                            # Handle nested Description field in TaxDetails
                            if "Description" in field.get("valueObject", {}):
                                desc = field.get("valueObject").get("Description")
                                field_data["Description"] = {
                                    "content": desc.get("content"),
                                    "confidence": desc.get("confidence")
                                }
                        
                        # Store the field
                        extracted[field_name] = field_data
                
                # Process Items separately (they're an array)
                items = fields.get("Items")
                if items:
                    items_array = []
                    
                    for item in items.get("valueArray", []):
                        item_data = {}
                        item_obj = item.get("valueObject", {})
                        
                        # Extract common item fields
                        item_fields = [
                            "Description", 
                            "Quantity",
                            "TotalPrice",
                            "UnitPrice",
                            "ProductCode"
                        ]
                        
                        for item_field in item_fields:
                            if item_field in item_obj:
                                item_data[item_field] = {
                                    "content": item_obj[item_field].get("content"),
                                    "confidence": item_obj[item_field].get("confidence")
                                }
                        
                        if item_data:
                            items_array.append(item_data)
                    
                    extracted["Items"] = {
                        "content": items_array,
                        "confidence": items.get("confidence", 0)
                    }
                
                # Add a simplified Category field from DocType
                if "DocType" in extracted:
                    doc_type = extracted["DocType"]
                    if "." in doc_type:
                        category = doc_type.split(".")[-1]
                        # Create a simplified Category field (e.g., "retailMeal" -> "Meal")
                        readable_category = category.removeprefix("retail").title()
                        extracted["Category"] = {
                            "content": readable_category,
                            "confidence": receipt.confidence if hasattr(receipt, "confidence") else 0
                        }
                
                # Store in Firestore
                receipt_id = db.collection("receipts").document()
                receipt_id.set(extracted)
                print(f"Saved to Firestore with ID: {receipt_id.id}")
                
                print("Analysis succeeded!")
                print("Results:", extracted)
            else:
                print("No receipt document found in the analysis")
            
        except Exception as e:
            print(f"Error with SDK call: {e}")
            import traceback
            traceback.print_exc()

# Run the function when script is executed directly
if __name__ == "__main__":
    analyze_receipt()