import openai
import easyocr
from pymongo import MongoClient
import json

# Configure OpenAI API Key
openai.api_key = "Your API Key"

# Step 1: Extract text using EasyOCR
def extract_text_with_easyocr(image_path):
    """
    Extract text from an image using EasyOCR.
    """
    reader = easyocr.Reader(["en"])
    results = reader.readtext(image_path, detail=0, paragraph=True)
    return "\n".join(results)


# Step 2: Use GPT to parse text into structured format
def parse_text_with_gpt(extracted_text):
    """
    Use GPT to parse the extracted text into a structured format.
    """
    prompt = f"""
    The following is the text extracted from a CV. Your task is to structure it into the required format below:

    Required Format:
    {{
        "Name": "<Name>",
        "Contact Information": {{
            "Email": "<Email>",
            "Phone": "<Phone>",
            "Address": "<Address>",
            "LinkedIn": "<LinkedIn>"
        }},
        "Skills": ["Skill1", "Skill2", "..."],
        "Experience": [
            {{
                "Role": "<Role>",
                "Company": "<Company>",
                "Duration": "<Start Date> - <End Date>",
                "Responsibilities": [
                    "Responsibility1",
                    "Responsibility2",
                    "..."
                ]
            }}
        ],
        "Education": [
            {{
                "Degree": "<Degree>",
                "Institution": "<Institution>",
                "Duration": "<Start Date> - <End Date>",
                "Details": "<Details>"
            }}
        ],
        "Certifications and Courses": ["Course1", "Course2", "..."],
        "Extra-Curricular Activities": ["Activity1", "Activity2", "..."]
    }}

    Here is the extracted text:
    {extracted_text}

    If any fields are empty, represent them as an empty list `[]` or an empty object `{{}}`.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that formats CVs."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0
    )
    try:
        # Parse the response JSON
        structured_data = json.loads(response['choices'][0]['message']['content'].strip())
        return structured_data
    except json.JSONDecodeError as e:
        print("Error: Invalid JSON format from GPT response.")
        print("Raw GPT Response:\n", response['choices'][0]['message']['content'])
        raise e


# Step 3: Save structured data into MongoDB
def save_to_mongodb(data):
    """
    Saves structured data into MongoDB in the required format.
    """
    # Connect to MongoDB
    client = MongoClient("mongodb+srv://user:user@kpi.900mg.mongodb.net/?retryWrites=true&w=majority&appName=KPI")
    db = client["CVDatabase"]
    collection = db["Resumes"]

    # Insert the data into MongoDB
    collection.insert_one(data)
    print("Data successfully inserted into MongoDB in the required format.")


# Main Function
if __name__ == "__main__":
    image_path = "cv2.jpg"  # Replace with your actual image path

    try:
        # Step 1: Extract text using EasyOCR
        extracted_text = extract_text_with_easyocr(image_path)
        print("Extracted Text:\n", extracted_text)

        # Step 2: Parse the extracted text using GPT
        structured_data = parse_text_with_gpt(extracted_text)
        print("\nStructured Data:\n", json.dumps(structured_data, indent=4))

        # Step 3: Save the structured data to MongoDB
        save_to_mongodb(structured_data)
    except Exception as e:
        print(f"Failed to process CV: {e}")
