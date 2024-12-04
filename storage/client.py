# Imports the Google Cloud client library
from google.cloud import storage

class StorageClient:
    def __init__(self, bucket):
        self.bucket_name = bucket
        
    def get_client(self):
        storage_client = storage.Client()
        self.client = storage_client.bucket(self.bucket_name)
        

    def uploadFile(self, file_name, file_path):
        self.get_client()
        blob = self.client.blob(file_name)
        try:
            blob.upload_from_filename(file_path, if_generation_match=0)
            return True
        except Exception as e:
            print(e)
            return False
        