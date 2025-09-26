import requests
import json

# Test the complete pipeline
data = {
    'content': '''AWS Lambda is a serverless compute service that lets you run code without provisioning or managing servers.
    Key benefits include automatic scaling, pay-per-use pricing, and support for multiple programming languages.
    Lambda functions can be triggered by various AWS services and integrate seamlessly with the AWS ecosystem.'''
}

try:
    response = requests.post('http://127.0.0.1:5000/api/analyze', json=data, timeout=60)
    print(f'Status Code: {response.status_code}')
    if response.status_code == 200:
        result = response.json()
        print('Success! Pipeline completed.')
        final_info = result.get('final_infographic', {})
        print(f'Final infographic URL: {final_info.get("image_url", "N/A")}')
        print(f'Platform: {final_info.get("platform", "N/A")}')
        print(f'Composition ID: {final_info.get("composition_id", "N/A")}')
    else:
        print(f'Error: {response.text}')
except Exception as e:
    print(f'Request failed: {e}')