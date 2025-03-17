# README

## Table of Contents
1. [Project Overview](#project-overview)  
2. [Key Features](#key-features)  
3. [Architecture](#architecture)  
4. [Prerequisites and Installation](#prerequisites-and-installation)  
5. [File Descriptions](#file-descriptions)  
6. [Usage](#usage)  
    - [1. Extract and Store CV Data (main.py)](#1-extract-and-store-cv-data-mainpy)  
    - [2. Analyze and Recommend Candidates (BestEmployee.py)](#2-analyze-and-recommend-candidates-bestemployeepy)  
7. [Configuration](#configuration)  
8. [Troubleshooting](#troubleshooting)  
9. [License](#license)  
10. [Contact](#contact)

---

## 1. Project Overview
This project automates the process of:
1. **Extracting text** from resume/CV images using **[EasyOCR](https://github.com/JaidedAI/EasyOCR)**.
2. **Parsing** the extracted text into a structured JSON format using **OpenAI’s GPT** (ChatGPT model).
3. **Storing** the parsed CV data in a **MongoDB** database.
4. **Analyzing** the stored CVs to:
   - Filter and match candidates to specific project criteria (e.g., relevant experience, skills, etc.).
   - Provide an enhanced matching score using GPT for final recommendations.
   - Suggest skill-growth paths for selected candidates.

This helps HR teams or hiring managers quickly identify the best candidates for a project or job opening and also guide them on skills to improve.

---

## 2. Key Features
- **EasyOCR** for CV text extraction (supports various image formats).
- **OpenAI GPT-3.5-turbo** for intelligent text parsing and candidate matching.
- **Fuzzy Matching** (using `fuzzywuzzy`) to identify relevant experience even with partial or approximate role matches.
- **TF-IDF Vectorization** for comparing candidate skills to project requirements.
- **MongoDB Integration** for storing and retrieving structured CV data.

---

## 3. Architecture

```
                +---------------------+
                |  CV Image (JPEG/PNG) 
                +---------+-----------+
                          |
                          v
                    [main.py]
                          |
         (EasyOCR + GPT)  |  Structured JSON
                          v
                     MongoDB
                          ^
                          |
                [BestEmployee.py]
    (FuzzyWuzzy + TF-IDF + GPT-based analysis)
                          |
                 Candidate Recommendations
                          |
         Skill Growth Recommendations (GPT)
```

1. **main.py**  
   - Reads an image using **EasyOCR**.  
   - Passes extracted text to **OpenAI GPT** for structured JSON output.  
   - Saves the resulting JSON to **MongoDB**.

2. **BestEmployee.py**  
   - Retrieves the structured CV data from **MongoDB**.  
   - Filters and ranks candidates using fuzzy matching and TF-IDF.  
   - Uses GPT to further refine the top candidate selection and recommend skill growth.

---

## 4. Prerequisites and Installation

### A. Environment
- **Python 3.7+** (Recommended to use a virtual environment)

### B. Libraries/Dependencies
Make sure you have the following packages installed:
1. **openai** (For GPT usage)  
2. **easyocr** (For text extraction from images)  
3. **pymongo** (For MongoDB connection)  
4. **numpy**  
5. **pandas**  
6. **scikit-learn** (For TF-IDF and cosine similarity)  
7. **fuzzywuzzy** (For fuzzy matching)  
8. **python-Levenshtein** (Required by fuzzywuzzy)  

You can install them via:
```bash
pip install openai easyocr pymongo numpy pandas scikit-learn fuzzywuzzy python-Levenshtein
```

### C. MongoDB
- A **MongoDB** instance or cluster is required.  
- Update your MongoDB connection URI in the scripts (`main.py` and `BestEmployee.py`) if needed.  

### D. OpenAI API Key
- Obtain your OpenAI API key from [OpenAI](https://platform.openai.com/).  
- Update the `openai.api_key` in both scripts or set it as an environment variable.

---

## 5. File Descriptions

1. **`main.py`**  
   - **Purpose**: Extract text from a CV image using EasyOCR, parse it into a structured format using GPT, and store it in MongoDB.  
   - **Key Steps**:  
     1. **Extract text** with EasyOCR.  
     2. **Parse** extracted text into JSON via GPT.  
     3. **Save** JSON to MongoDB.

2. **`BestEmployee.py`**  
   - **Purpose**: Retrieve stored CVs from MongoDB, filter candidates, compute similarity scores, and use GPT to enhance matching & recommend skill growth.  
   - **Key Steps**:  
     1. **Retrieve** resumes from MongoDB.  
     2. **Filter** by relevant experience using fuzzy matching.  
     3. **TF-IDF** to vectorize candidate skills & compare to project requirements.  
     4. **GPT** for final ranking & skill growth suggestions.

3. **Sample CV Images** (e.g., `cv_image.jpg`, `cv2.jpg`)  
   - **Purpose**: Example CVs to demonstrate how the scripts process real-world data.  

---

## 6. Usage

### 1. Extract and Store CV Data (`main.py`)

1. **Place** your CV images in the same directory (or specify the correct path in `main.py`).
2. **Open** `main.py` and locate the line:
   ```python
   image_path = "cv2.jpg"  # Replace with your actual image path
   ```
   Update it with the correct file name/path.
3. **Run** the script:
   ```bash
   python main.py
   ```
4. **Check** the console output to confirm that:
   - Text was extracted by EasyOCR.  
   - The structured JSON was generated by GPT.  
   - The data was successfully inserted into MongoDB.

### 2. Analyze and Recommend Candidates (`BestEmployee.py`)

1. **Open** `BestEmployee.py` and review the **Project Criteria** dictionary (inside `if __name__ == "__main__":`) to ensure it matches your use case:
   ```python
   project_criteria = {
       "languages": "Java",
       "duration": "6 months",
       "people_count": 1,
       "field": "Software Engineer"
   }
   ```
   - `languages`: The required programming language(s) or technology stack.  
   - `duration`: Project duration.  
   - `people_count`: Number of candidates to select.  
   - `field`: The role or domain to filter by (e.g., "Software Engineer").
2. **Run** the script:
   ```bash
   python BestEmployee.py
   ```
3. **Observe** the console output for:
   - Filtered candidates based on fuzzy matching of the `field`.  
   - TF-IDF similarity scores.  
   - GPT’s final selection of top candidates.  
   - GPT’s recommendations for skill growth.

---

## 7. Configuration

1. **OpenAI API Key**  
   - In both `main.py` and `BestEmployee.py`, locate:
     ```python
     openai.api_key = "Your API Key"
     ```
   - Replace `"Your API Key"` with your actual API key or set it as an environment variable:
     ```bash
     export OPENAI_API_KEY="sk-xxxxxxxx"
     ```
     Then, in the scripts, you can do:
     ```python
     import os
     openai.api_key = os.getenv("OPENAI_API_KEY")
     ```

2. **MongoDB Connection**  
   - In both scripts, locate the connection string:
     ```python
     MongoClient("mongodb+srv://user:user@kpi.900mg.mongodb.net/?retryWrites=true&w=majority&appName=KPI")
     ```
   - Replace with your own MongoDB URI if necessary. For local setups:
     ```python
     MongoClient("mongodb://localhost:27017/")
     ```
     Make sure the database (`CVDatabase`) and collection (`Resumes`) exist or are created automatically by insertion.

3. **Fuzzy Matching Threshold**  
   - Within `BestEmployee.py`, you’ll see:
     ```python
     if similarity > 70:
     ```
   - Adjust the threshold to increase or decrease strictness for matching roles (e.g., “Software Engr.” vs. “Software Engineer”).

---

## 8. Troubleshooting

- **No module named ‘easyocr’**:  
  Ensure `easyocr` is installed. Run `pip install easyocr`.
- **OpenAI authentication error**:  
  Check your **API key**. Make sure you have sufficient credits or usage quota.
- **Invalid JSON format from GPT**:  
  Occurs if GPT returns unstructured or malformed JSON. You can add more guidance to the prompt or handle parsing exceptions more robustly.
- **MongoDB connection issues**:  
  Ensure your connection string is correct, the database is accessible, and you have the right permissions.

---

## 9. License
You can include your chosen license here (e.g., MIT, Apache 2.0, etc.) or remove this section if not applicable.

---

## 10. Contact
