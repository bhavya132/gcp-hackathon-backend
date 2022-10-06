
import os

from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict

import base64


class GarbagePredictor:
    def __init__(self):
        self.endpoint_id ="7707633685314404352"  #os.environ.get('MLENDPOINT')
        self.location ="us-central1"# os.environ.get('MLLOCATION')
        self.project= "25539515225" #os.environ.get('MLPROJECT')
        # The AI Platform services require regional API endpoints.
        api_endpoint = 'us-central1-aiplatform.googleapis.com'
        client_options = {"api_endpoint": api_endpoint}
         # Initialize client that will be used to create and send requests.
        # This client only needs to be created once, and can be reused for multiple requests.
        self.client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)


    def make_prediction(self,filename):
         
        with open(filename, "rb") as f:
            file_content = f.read()
        # The format of each instance should conform to the deployed model's prediction input schema.
        encoded_content = base64.b64encode(file_content).decode("utf-8")
        instance = predict.instance.ImageClassificationPredictionInstance(
            content=encoded_content,
        ).to_value()
        instances = [instance]
        # See gs://google-cloud-aiplatform/schema/predict/params/image_classification_1.0.0.yaml for the format of the parameters.
        parameters = predict.params.ImageClassificationPredictionParams(
            confidence_threshold=0.5, max_predictions=5,
        ).to_value()
        endpoint = self.client.endpoint_path(
            project=self.project, location=self.location, endpoint=self.endpoint_id
        )
        response = self.client.predict(
            endpoint=endpoint, instances=instances, parameters=parameters
        )
        print("response")
        print(" deployed_model_id:", response.deployed_model_id)
        # See gs://google-cloud-aiplatform/schema/predict/prediction/image_classification_1.0.0.yaml for the format of the predictions.
        predictions = response.predictions
        for prediction in predictions:
            print(" prediction:", dict(prediction))
        print(predictions[0]['displayNames'][0])
        os.remove(filename)
        return dict(predictions[0])

    def classify(self, imgData):
        result=self.make_prediction(imgData)
        
        ans=result['displayNames'][0]
        if(ans=="recycle"):
                return "Recyclable"
        elif(ans=="organic"):
            return "Organic"
        else:
            return "Not Recyclable"
    

        
gp = GarbagePredictor()
