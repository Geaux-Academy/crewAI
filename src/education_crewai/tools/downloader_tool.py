import os
import requests
import openai
from crewai_tools import tool

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

@tool
def download_and_store_in_blob(url, subject, grade_level):
    """
    Downloads content from the given URL, processes it using OpenAI,
    and stores the processed content in Vercel Blob, organized by subject and grade level.
    """
    try:
        # Download the content
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses

        # Process content using OpenAI (e.g., summarization)
        content_summary = (
            openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Summarize the following content: {response.text}",
                max_tokens=150,
            )
            .choices[0]
            .text.strip()
        )

        # Generate a filename based on the URL
        filename = url.split("/")[-1] or "processed_content.txt"

        # Vercel Blob URL and Headers
        blob_api_url = f"https://api.vercel.com/v1/blob"  # Adjust this URL based on the actual Vercel Blob API endpoint
        headers = {
            "Authorization": f"Bearer {os.getenv('BLOB_READ_WRITE_TOKEN')}",  # Use the token from the environment
            "Content-Type": "application/octet-stream",
        }

        # Upload the content to Vercel Blob
        blob_response = requests.post(
            blob_api_url,
            headers=headers,
            data=content_summary.encode('utf-8'),  # Ensure your content is encoded as needed
            params={"filename": f"{subject}/{grade_level}/{filename}"}  # Adjust parameters based on the Vercel API documentation
        )

        if blob_response.status_code == 200:
            return f"Successfully processed and stored content in Vercel Blob under {subject}/{grade_level}/{filename}"
        else:
            return f"Failed to store content in Vercel Blob: {blob_response.text}"

    except requests.exceptions.RequestException as e:
        return f"Failed to download content from {url}: {e}"
    except openai.error.OpenAIError as e:
        return f"Failed to process content using OpenAI: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"
