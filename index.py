import os
import json
from docx import Document
from openai import OpenAI

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

def read_word_file(file_path):
    doc = Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

file_path = './FS_DOC.docx'
content = read_word_file(file_path)

test_topics = client.chat.completions.create(
    model="gpt-3.5-turbo-0125",
    response_format={ "type": "json_object" },
    messages=[
        {"role": "system", "content": "You are a QA engineer at a software company. You are reviewing a document that contains a list of requirements for a new feature. You need to provide only topics and descriptions for test cases in JSON format."},
        {"role": "user", "content": content},
        {"role": "assistant", "content": "How should be JSON file be structured?"},
        {"role": "user", "content": "JSON object should contain test_cases object as array with objects. Each object in array should contain topic: string and description: string fields"},
    ]
)

test_topic_output = test_topics.choices[0].message.content

if isinstance(test_topic_output, str):
    test_topic_output = json.loads(test_topic_output)
else:
    test_topic_output = test_topic_output  

print("Test topics have been created")

test_cases = []

for topic in test_topic_output["test_cases"]:
    print("creating test case for topic: ", topic["topic"])
    new_test_case = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "You are a QA engineer at a software company. You are reviewing a document that contains a list of requirements for a new feature. You need to provide test case for the given topic: {topic} as JSON object."},
            {"role": "user", "content": content},
            {"role": "assistant", "content": "How should be JSON file be structured?"},
            {"role": "user", "content": "It should be JSON object that contain the following fields: description: string, preconditions: arr[string], test_data: string, execution_steps: arr[string], expected_result: arr[string]."},
        ]
    )

    new_test_case_output = new_test_case.choices[0].message.content

    if isinstance(new_test_case_output, str):
        new_test_case_output = json.loads(new_test_case_output)
    else:
        new_test_case_output = new_test_case_output  
    
    test_cases.append(new_test_case_output)

def get_test_case_string(test_case):
    return f"""
--------------------------------------------
## Test description: {test_case["description"]}

## Preconditions: 
{'\n'.join(test_case['preconditions'])}

## Test Data: 
{test_case['test_data']}

## Execution Steps: 
{'\n'.join(test_case['execution_steps'])}

## Expected Result: 
{'\n'.join(test_case['expected_result'])}

--------------------------------------------
"""

file_name_test_cases = "test_cases.txt"

with open(file_name_test_cases, 'w') as f:
    for test_case in test_cases:
        f.write(get_test_case_string(test_case))
        f.write("\n")

print(f"Test cases have been written to {file_name_test_cases}")