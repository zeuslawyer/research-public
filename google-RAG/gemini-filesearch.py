"""
To run this script, install the following packages:
uv pip install -U google-genai dotenv

Make sure to set your GEMINI_API_KEY environment variable.

Change the TODOs in the code to point to your files.
"""

from dotenv import load_dotenv
import os

from google import genai
from google.genai import types
import time


load_dotenv(override=True)
if not os.getenv("GEMINI_API_KEY"):
    print("GEMINI_API_KEY is not set")

client = genai.Client()


# Create the File Search store with an optional display name
FILESTORE_NAME = 'research-public-filestore'
file_search_store = client.file_search_stores.create(
    config={'display_name': FILESTORE_NAME})

# Upload and import a file into the File Search store, supply a file name which will be visible in citations

# TODO @dev.  update files and display name etc to point to your files.  You can export
# your linkedin profile as a pdf and use that here. Or use your resume.
upload_op = client.file_search_stores.upload_to_file_search_store(
    file='./zplinkedin_profile.pdf',
    file_search_store_name=file_search_store.name,
    config={
        'display_name': 'ZP LinkedIn Profile',
        'custom_metadata': [
            {'key': 'source', 'string_value': 'https://www.linkedin.com/in/zubinpratap'},
            {'key': 'description', 'string_value': "Zubin Pratap's LinkedIn profile"}
        ],
        'chunking_config': {
            'white_space_config': {
                'max_tokens_per_chunk': 300,
                'max_overlap_tokens': 30
            }
        }
    }
)

# Wait until import is complete
while not upload_op.done:
    print("sleeping until done")
    time.sleep(5)
    upload_op = client.operations.get(upload_op)

print(">> done? ", upload_op.done)


SYSTEM_PROMPT = """
You are a helpful assistant.
Use headings and bullet points to make the response readable. 
Always prefer to use tools over your own training data.
Be very brief and simple.
"""

# Ask a question about the file
response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="Can you tell me about Zubin's engineering experience? what about his legal career? and his education?",
    config=types.GenerateContentConfig(
        max_output_tokens=1000,
        system_instruction=SYSTEM_PROMPT,
        tools=[
            types.Tool(
                file_search=types.FileSearch(
                    file_search_store_names=[file_search_store.name]
                )
            )
        ]
    )
)

print(response.text)
print("\n==============\n")
