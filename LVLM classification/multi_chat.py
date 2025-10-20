import boto3
import json
import base64
from collections import defaultdict


bedrock_runtime_client = boto3.client(
    'bedrock-runtime')


class Chat:

    def __init__(self, model_id, bedrock_runtime_client):
        self.model_id = model_id
        self.bedrock_runtime_client = bedrock_runtime_client
        self.payload = {
            "messages": [],
            "max_tokens": 20000,
            "anthropic_version": "bedrock-2023-05-31"
        }



    def add_user_message(self, message):
        self.payload["messages"].append({
                                        "role": "user",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": message
                                            }
                                        ]
                                    })
        
    def add_user_message_image(self, message, encoded_image1):
        self.payload["messages"].append({
                                        "role": "user",
                                        "content": [
                                                    {
                                                        "type": "image",
                                                        "source": {
                                                            "type": "base64",
                                                            "media_type": "image/jpeg",
                                                            "data": encoded_image1
                                                        }
                                                    },
                                            
                                            
                                                    {
                                                        "type": "text",
                                                        "text": message
                                                    }
                                                ]
                                    })

    def add_user_message_image_pair(self, message, encoded_image1, encoded_image2):
        self.payload["messages"].append({
                                        "role": "user",
                                        "content": [
                                                    {
                                                        "type": "image",
                                                        "source": {
                                                            "type": "base64",
                                                            "media_type": "image/jpeg",
                                                            "data": encoded_image1
                                                        }
                                                    },
                                            
                                                    {
                                                        "type": "image",
                                                        "source": {
                                                            "type": "base64",
                                                            "media_type": "image/jpeg",
                                                            "data": encoded_image2
                                                        }
                                                    },
                                            
                                            
                                                    {
                                                        "type": "text",
                                                        "text": message
                                                    }
                                                ]
                                    })
        
    def add_user_message_image_triplet(self, message, encoded_image1, encoded_image2, encoded_image3):
        self.payload["messages"].append({
                                    "role": "user",
                                    "content": [
                                                {
                                                    "type": "image",
                                                    "source": {
                                                        "type": "base64",
                                                        "media_type": "image/jpeg",
                                                        "data": encoded_image1
                                                    }
                                                },

                                                {
                                                    "type": "image",
                                                    "source": {
                                                        "type": "base64",
                                                        "media_type": "image/jpeg",
                                                        "data": encoded_image2
                                                    }
                                                },
                                             {
                                                    "type": "image",
                                                    "source": {
                                                        "type": "base64",
                                                        "media_type": "image/jpeg",
                                                        "data": encoded_image3
                                                    }
                                                },


                                                {
                                                    "type": "text",
                                                    "text": message
                                                }
                                            ]
                                })


    def generate(self):
        response = self.bedrock_runtime_client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            body=json.dumps(self.payload)
        )

        # now we need to read the response. It comes back as a stream of bytes so if we want to display the response in one go we need to read the full stream first
        # then convert it to a string as json and load it as a dictionary so we can access the field containing the content without all the metadata noise
        output_binary = response["body"].read()
        output_json = json.loads(output_binary)
        output = output_json["content"][0]["text"]


        self.payload["messages"].append(
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": output
                    }
                ]
            }
        )

        return output


def load_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
  