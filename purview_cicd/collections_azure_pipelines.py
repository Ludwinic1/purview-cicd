import os
from auth import get_access_token
from request_utils import (
    get_request,
    put_request,
    post_request
)


def main():
    SOURCE_CLIENT_ID = os.environ["SOURCE_PURVIEW_CLIENT_ID"]
    SOURCE_CLIENT_SECRET = os.environ["SOURCE_PURVIEW_CLIENT_SECRET"]
    SOURCE_TENANT_ID = os.environ["SOURCE_TENANT_ID"]
    TARGET_CLIENT_ID = os.environ["TARGET_PURVIEW_CLIENT_ID"]
    TARGET_CLIENT_SECRET = os.environ["TARGET_PURVIEW_CLIENT_SECRET"]
    TARGET_TENANT_ID = os.environ["TARGET_TENANT_ID"]
    SOURCE_PURVIEW_ACCOUNT_NAME = os.environ["SOURCE_PURVIEW_ACCOUNT_NAME"]
    TARGET_PURVIEW_ACCOUNT_NAME = os.environ["TARGET_PURVIEW_ACCOUNT_NAME"]

    # Define the config variables
    source_collections_endpoint = f"https://{SOURCE_PURVIEW_ACCOUNT_NAME}.purview.azure.com/account/collections"
    target_collections_endpoint = f"https://{TARGET_PURVIEW_ACCOUNT_NAME}.purview.azure.com/account/collections"
    collections_api_version = "2019-11-01-preview"

    # Acquire access token for source Purview
    access_token = get_access_token(SOURCE_TENANT_ID, SOURCE_CLIENT_ID, SOURCE_CLIENT_SECRET)
    headers = { 
        "Authorization": f"Bearer {access_token}",
        'Content-Type': 'application/json',
    }
    # Acquire access token for target Purview
    target_purview_access_token = get_access_token(TARGET_TENANT_ID, TARGET_CLIENT_ID, TARGET_CLIENT_SECRET)
    target_headers = {
        "Authorization": f"Bearer {target_purview_access_token}",
        'Content-Type': 'application/json',
    }
     
    def create_collection(collection: str, parent_collection_name: str = None):
        collection_info = get_request(url=f"{source_collections_endpoint}/{collection}?api-version={collections_api_version}", headers=headers)
        
        if not parent_collection_name:
            parent_collection_name = collection_info["parentCollection"]["referenceName"]

        if "description" in collection_info:
            body = {
                "friendlyName": collection_info["friendlyName"],
                "description": collection_info["description"],
                "parentCollection": {
                    "referenceName": parent_collection_name
                }
            }
        else:
            body = {
                "friendlyName": collection_info["friendlyName"],
                "parentCollection": {
                    "referenceName": parent_collection_name
                }
            }
        
        create_collection_request = put_request(url=f"{target_collections_endpoint}/{collection}?api-version={collections_api_version}", headers=target_headers, body=body) 
        return create_collection_request

    # Find the target Purview root collection name
    existing_target_collections = get_request(url=f"{target_collections_endpoint}?api-version={collections_api_version}", headers=headers)
    target_root_real_name = [coll["name"] for coll in existing_target_collections["value"] if "parentCollection" not in coll][0]

    collections = get_request(url=f"{source_collections_endpoint}?api-version={collections_api_version}", headers=headers)

    root_real_name = [coll["name"] for coll in collections["value"] if "parentCollection" not in coll][0]
    root_children = [coll["name"] for coll in collections["value"] if "parentCollection" in coll and coll["parentCollection"]["referenceName"] == root_real_name.lower()] # Purview lowercases the parent collection name under the hood
        
    # Create the root children collections first
    for coll in root_children:
        create_collection(collection=coll, parent_collection_name=target_root_real_name)
    
    def create_child_collections(collection: str):
        """Recursively create all of the children in a given collection hierarchy"""
        child_list = []
        child_collections = get_request(url=f"{source_collections_endpoint}/{collection}/getChildCollectionNames?api-version={collections_api_version}", headers=headers)
        if child_collections["count"] > 0:
            for child in child_collections["value"]:
                child_list.append(child["name"])
                create_collection(collection=child["name"]) 
        for child in child_list:
            create_child_collections(collection=child) # recursively calls the function to find and create all of the children in the hierarchy
            child_list.remove(child) # once a full collection hierarchy is created, remove the collection

    for coll in root_children:
        create_child_collections(collection=coll)

if __name__ == "__main__":
    main()


