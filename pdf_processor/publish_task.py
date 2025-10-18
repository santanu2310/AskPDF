import os
import sys

# Add the current directory to the python path to allow imports from `app`
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.tasks.process_pdf import process_pdf

if __name__ == "__main__":
    # This will send a message to the SQS queue that the celery worker is listening to.
    # You can then use the AWS CLI to view the message in the queue.
    # Replace with a real doc_id and key if you want the task to be processed.
    result = process_pdf.delay(doc_id="test_doc_id", key="test_key")
    print(f"Task sent with id: {result.id}")
