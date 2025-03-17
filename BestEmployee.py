import openai
from pymongo import MongoClient
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz

# Set OpenAI API Key
openai.api_key = "Your API Key"

# Step 1: Retrieve Data from MongoDB
def retrieve_data_from_mongodb():
    """
    Connect to MongoDB and retrieve all resumes.
    """
    client = MongoClient("mongodb+srv://user:user@kpi.900mg.mongodb.net/?retryWrites=true&w=majority&appName=KPI")
    db = client["CVDatabase"]
    collection = db["Resumes"]

    # Retrieve all data
    resumes = list(collection.find({}))
    return pd.DataFrame(resumes)

# Step 2: Filter Employees by Experience
def filter_employees_by_experience(data, field):
    """
    Filter employees based on their experience in the given field using fuzzy matching.
    """
    def has_relevant_experience(experience_list):
        # Use fuzzy matching to find relevant roles
        for exp in experience_list:
            role = exp.get("Role", "")
            similarity = fuzz.partial_ratio(field.lower(), role.lower())
            print(f"Checking role '{role}' against field '{field}' with similarity {similarity}")
            if similarity > 70:  # Threshold for fuzzy matching
                return True
        return False

    # Filter the data based on relevant experience
    filtered_data = data[data['Experience'].apply(has_relevant_experience)]
    print("\nFiltered Data:\n", filtered_data)
    return filtered_data

# Step 3: Preprocess Data with TF-IDF
def preprocess_data(data):
    """
    Preprocess the skills data using TF-IDF.
    - Convert lists into strings.
    - Handle missing or empty values.
    """
    try:
        # Ensure Skills is a string
        data['Skills'] = data['Skills'].apply(
            lambda x: " ".join(x) if isinstance(x, list) else x
        )
        data['Skills'] = data['Skills'].fillna("")  # Replace NaN with an empty string

        # Debug print for Skills column
        print("\nSkills column after preprocessing:\n", data['Skills'].head())

        # Initialize TF-IDF vectorizer
        vectorizer = TfidfVectorizer()
        data['Skills_Vector'] = list(vectorizer.fit_transform(data['Skills']).toarray())

        # Debug print for Skills_Vector
        print("\nSkills_Vector created:\n", data['Skills_Vector'][:5])

        return data, vectorizer
    except Exception as e:
        print(f"Error in preprocess_data: {e}")
        raise


# Step 4: Use OpenAI for Enhanced Matching
# Step 4: Use OpenAI for Enhanced Matching
def enhance_matching_with_openai(project_criteria, candidates):
    """
    Use OpenAI's GPT to enhance candidate matching for the project.
    """
    try:
        prompt = f"""
        You are a hiring assistant. Match the best-suited candidates for the project based on the following criteria:

        Project Criteria:
        {{
            "Languages": "{project_criteria['languages']}",
            "Duration": "{project_criteria['duration']}",
            "People Required": "{project_criteria['people_count']}",
            "Relevant Field": "{project_criteria['field']}"
        }}

        Candidate Data:
        {candidates.to_dict(orient='records')}

        Provide the top {project_criteria['people_count']} candidates based on relevance to the criteria.
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for candidate matching."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0
        )
        # Return result without printing here
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error in enhance_matching_with_openai: {e}")
        raise

# Step 5: Recommend Skills for Growth
def recommend_skills_for_growth(selected_candidates, project_criteria):
    """
    Use OpenAI to recommend skills, languages, or technologies for selected candidates to pursue.
    """
    try:
        prompt = f"""
        You are a career advisor. Based on the following project requirements and selected candidates' skills, recommend skills, languages, or technologies they should pursue to grow in their career.

        Project Requirements:
        {{
            "Languages": "{project_criteria['languages']}",
            "Relevant Field": "{project_criteria['field']}"
        }}

        Selected Candidates:
        {selected_candidates.to_dict(orient='records')}

        Provide detailed recommendations for each candidate.
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful career advisor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            temperature=0
        )
        # Return result without printing here
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error in recommend_skills_for_growth: {e}")
        raise



# Step 6: Match Candidates for a Project
def find_best_employees_and_recommend_skills(project_criteria, data, vectorizer):
    """
    Find the best employees for the given project criteria and recommend skills for growth.
    """
    try:
        # Filter data by relevant experience
        filtered_data = filter_employees_by_experience(data, project_criteria['field'])
        if filtered_data.empty:
            return "No candidates found with relevant experience.", None

        # Convert project skills into vector
        project_skills_vector = vectorizer.transform([project_criteria['languages']]).toarray()

        # Compute cosine similarity between project skills and candidate skills
        similarities = cosine_similarity(project_skills_vector, np.vstack(filtered_data['Skills_Vector']))

        # Add similarity scores to the DataFrame
        filtered_data['Similarity'] = similarities[0]

        # Sort by similarity score
        sorted_candidates = filtered_data.sort_values(by='Similarity', ascending=False).head(project_criteria['people_count'])

        # Debug: Check sorted candidates
        print("\nSorted Candidates:\n", sorted_candidates)

        # Enhance recommendations using OpenAI
        enhanced_results = enhance_matching_with_openai(project_criteria, sorted_candidates)
        if not isinstance(enhanced_results, str):
            print("\nEnhanced Results:\n", enhanced_results)

        # Recommend skills for growth
        skill_recommendations = recommend_skills_for_growth(sorted_candidates, project_criteria)
        if not isinstance(skill_recommendations, str):
            print("\nSkill Recommendations:\n", skill_recommendations)

        return enhanced_results, skill_recommendations

    except Exception as e:
        print(f"Error in find_best_employees_and_recommend_skills: {e}")
        raise


# Main Function
if __name__ == "__main__":
    try:
        # Retrieve resumes from MongoDB
        data = retrieve_data_from_mongodb()
        print("Resumes retrieved from MongoDB:\n", data.head())

        # Define project criteria
        project_criteria = {
            "languages": "Java",
            "duration": "6 months",
            "people_count": 1,
            "field": "Software Engineer"
        }

        # Preprocess the data
        try:
            data, vectorizer = preprocess_data(data)
            print("\nPreprocessed Data:\n", data[['Skills', 'Skills_Vector']].head())
        except Exception as preprocess_error:
            print(f"Error during preprocessing: {preprocess_error}")
            raise

        # Find the best employees and recommend skills
        try:
            recommendations, skill_recommendations = find_best_employees_and_recommend_skills(
                project_criteria, data, vectorizer
            )
            # Print final outputs
            print("\nTop Recommendations:\n", recommendations)
            print("\nSkill Recommendations for Growth:\n", skill_recommendations)
        except Exception as matching_error:
            print(f"Error during employee matching: {matching_error}")
            raise

    except Exception as e:
        print(f"Error occurred: {e}")
