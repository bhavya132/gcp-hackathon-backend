from concurrent.futures import process
import os, uuid

connect_str = os.getenv('STORAGE_CONN')



from google.cloud import storage

json={
  "type":os.environ.get('type'), 
  "project_id":os.environ.get('project_id') ,
  "private_key_id": os.environ.get('private_key_id'),
  "private_key":os.environ.get('private_key'),
  "client_email": os.environ.get('client_email'),
  "client_id": os.environ.get('client_id'),
  "auth_uri":os.environ.get('auth_uri') ,
  "token_uri": os.environ.get('token_uri'),
  "auth_provider_x509_cert_url": os.environ.get('auth_provider_x509_cert_url'),
  "client_x509_cert_url": os.environ.get('client_x509_cert_url')
}
p=os.path.abspath("serving_key.json.env")
client = storage.Client.from_service_account_json(p)

bucket = client.get_bucket('hariyali_profile')

class CloudStorage:
    @classmethod
    def upload(self, filepath, filename):
       
        object_name_in_gcs_bucket = bucket.blob(filename)
        object_name_in_gcs_bucket.upload_from_filename(filepath)
        return "https://storage.googleapis.com/hariyali_profile/" + filename


