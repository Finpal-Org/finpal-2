# import libraries
from dataclasses import field
from datetime import date
import datetime
from multiprocessing.managers import ValueProxy
import os
#REST api imports
import requests
import time
#ENV 
from dotenv import load_dotenv
#import firestore
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

load_dotenv() # access env

cred = credentials.Certificate(os.getenv("FIREBASE_KEY_PATH")) # private credentails
firebase_admin.initialize_app(cred) #init app with our project cred
db = firestore.client() # connect to db


#Endpoint & Key from azur
endpoint = os.getenv("AZURE_ENDPOINT")
key = os.getenv("AZURE_KEY")

analyze_url = f"{endpoint}documentintelligence/documentModels/prebuilt-receipt:analyze?api-version=2024-11-30"

def analyze_receipt():
    # Path to the receipt file - make sure this is the correct path and a < 4mb size  
    receipt_path = "../assets/receipt1.jpg"
        
    # Open the receipt img in binary mode (required by azure)
    with open(receipt_path, "rb") as f: #rb: read binary
        # Read the file content
        receipt_data = f.read()
        
        print(f"File size: {len(receipt_data) / (1024 * 1024):.2f} MB")
                
       
        #exact url from azure docs
        analyze_url = f"{endpoint}documentintelligence/documentModels/prebuilt-receipt:analyze?api-version=2024-11-30"
        #these are info azure needs to be passed in post request
        headers = {
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "image/jpeg"
        }
        
        print("\nAnalyzing receipt using direct REST API...")
        try:
            # Step 1: Send the image to Azure for analysis
            response = requests.post(analyze_url, headers=headers, data=receipt_data)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 202:  # operation Accepted, operation started
                # Get the operation-location URL to check the operation status (ticket number) 
                operation_location = response.headers.get("Operation-Location")
                print(f"Operation started at: {operation_location}")
                
                # Step 2: Poll until the analysis is complete 
                if operation_location:
                    poll_headers = {
                        "Ocp-Apim-Subscription-Key": key
                    }
                    #(repeated checking)
                    # print("\nPolling operation...")
                    for _ in range(10):  # Poll up to 10 times, doesnt actually drain request
                        time.sleep(2)  # Wait 2 seconds between polls
                        #result?
                        operation_response = requests.get(operation_location, headers=poll_headers)
                        # print(f"Poll status code: {operation_response.status_code}")
                        
                        if operation_response.status_code == 200:#operation result returned
                            # result in json? TODO: extract need fields only from this complex result
                            result = operation_response.json()
                            status = result.get("status")
                            # print(f"Operation status: {status}")

                            if status == "succeeded":
                                print("Analysis succeeded!")
                                extracted= extracted_result(result)
                                # print("Results:", extracted) #show results
                                break
                            elif status == "failed":
                                print("Analysis failed:", extracted)
                                break
                        else:
                            print(f"Error response: {operation_response.text}")
                            break
            else:
                print(f"Error response: {response.text}")
        except Exception as e:
            print(f"Error with REST API call: {e}")


def extracted_result(result):
    #extract only needed fields from azure results
    extracted = {}

    # DEBUG TODO - print the structure of the result
    print("\nAPI RESPONSE STRUCTURE:")
        
    if "analyzeResult" in result:
        analyze_result = result.get("analyzeResult", {})
        # print("Keys in analyzeR  esult:", analyze_result.keys())
        
        if "documents" in analyze_result:
            documents = analyze_result.get("documents", [])
            # if documents:
                # print("Document type:", documents[0].get("docType", "No docType found"))
                # print("Document type:", documents[0].get("ReceiptType", "No ReceiptType found"))
                # print("Document fields available:", documents[0].get("fields", {}).keys())

    try: 
        #navigate to doc fields (todo , {})
        documents = result.get("analyzeResult",{}).get("documents",[])
        if not documents:
            return{"error": "No docs found in azure result"}

        #1st document (the Result)
        document = documents[0]  # Get the document object (without fields)

        fields = documents[0].get("fields",{})
#todo transportation (car) is Transportation.CarRental change it..
        # 1.Needed fields & mapping names (renaming azure's naming to our preffered naming)
        field_mapping = {
            # vendor object
            "vendor": {
                "name": "MerchantName",
                "address": "MerchantAddress",
                "phone": "MerchantPhoneNumber"
            },
            # date and time
            "date": "TransactionDate",
            "time": "TransactionTime",
            
            # money values
            "total": "Total",
            "subtotal": "Subtotal", 
            "tax": "TotalTax",
            
            # other fields
            "tip": "Tip",
            "payment": {
                "type": "PaymentType"
            },
            "currency": "currencyCode",
            "invoice_number": "TransactionId",
            "line_items": "Items",
            "category": "ReceiptType"
        }

        # 2. extract content & confidence fields
        for our_field, azure_field in field_mapping.items():
            if azure_field in fields: #if u found azure field
                field_obj= fields[azure_field] #azure field added to field_obj 

                extracted[our_field]={  #in extracted , match extracted field data from azure(content,confidence) to our_field 
                    "content":field_obj.get("content",""),
                    "confidence": field_obj.get("confidence",0)
                }

        receiptType = "ReceiptType" # category
        if("ReceiptType" in fields):
            extracted["category"] = {
                "content": fields["ReceiptType"].get("valueString","Other"), # get value of category, store it in valueStr key -> other if empty..
                "confidence": fields["ReceiptType"].get("confidence",0)
            }

        # 3. COMPLEX ITEMS HANDLING (more nested)
        if "Items" in fields:
            items_field = fields["Items"]
            items_array = []
            
            if "valueArray" in items_field:
                for i, item in enumerate(items_field.get("valueArray", [])):
                    item_properties = {}
                    
                    # The structure is valueObject, not properties
                    if "valueObject" in item:
                        value_obj = item["valueObject"]
                        
                        # Add id field (using index if no ID is available)
                        item_properties["id"] = i + 1

                        if "Description" in value_obj:
                            item_properties["description"] = value_obj["Description"].get("content", "")
                        
                        if "Quantity" in value_obj:
                            item_properties["quantity"] = value_obj["Quantity"].get("content", "1")
                        
                        if "TotalPrice" in value_obj:
                            item_properties["total"] = value_obj["TotalPrice"].get("content", "0")
                    
                    items_array.append(item_properties)
            
            extracted["line_items"] = items_array

        #Tags 
        if "Tags" in analyze_result:
            extracted["tags"]= analyze_result.get("Tags", {})

        #Doctype / Category 
        if "docType" in document:
            doc_type= document.get("docType","") 
            extracted["category"] = doc_type.split(".")[-1] if "." in doc_type else doc_type


    #exception
    except Exception as e:
        return {"error": f"Extracting fields error: {str(e)}" }

    # Firestore the receipt
    if(extracted):
        current_time = datetime.datetime.now()
        extracted["createdTime"]= current_time # add new key (creation time) inside extract -> store created time in db

        receipt_id = db.collection("receipts").document() # add receipt with random id
        receipt_id.set(extracted) # set new doc with fresh extracted receipt data
        

    return extracted
#end of extracted_result ...


# Run the function when script is executed directly
if __name__ == "__main__":
    analyze_receipt()