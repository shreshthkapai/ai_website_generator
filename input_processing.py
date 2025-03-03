from openai import OpenAI
import json
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")
MODEL = "gpt-4o"

openai = OpenAI(api_key=openai_api_key)

def process_user_input(prompt, image_data, image_prompts):
    structured_prompt = f"""
Based on this user prompt:

{prompt}

Analyze the request carefully and extract structured data **without using hardcoded rules**. Infer content intelligently based on meaning and context.

🔹 **ADDITIONAL KEY ANALYSIS**
- **Determine Website Structure**: Identify if the user wants a multi-page website or a single-page website with sections.
  - Look for phrases like "multiple pages", "separate pages", "different pages", or specific page names.
  - If the user mentions different pages by name (e.g., "home page", "contact page"), infer a multi-page structure.
  - Include a "website_structure" field in your response with value "multi-page" or "single-page".
  - For multi-page websites, include a "pages" array with the names of all required pages.
  
🔹 **STRICT RULES**  
- **Infer categories logically** (e.g., Work Experience vs. Projects) instead of relying on predefined keywords.  
- **Recognize the website type from the prompt** and structure content accordingly.  
- If all necessary details are provided, **use them exactly** without generating extra content.  
- If details are missing, **fill in gaps naturally based on context** (e.g., an e-commerce site without product details should still generate example products).  

🔹 **1. Understand Website Type & Purpose**  
- Identify whether the website is a **portfolio, business, landing page, or e-commerce site** based on the user's prompt.  
- Structure sections accordingly **without requiring explicit section names** from the user.  

🔹 **2. Extract & Organize Content Dynamically**  
- **Infer content meaning based on context**, not predefined labels.  
  - Work Experience should contain **career-related details** (e.g., job roles, company names).  
  - Projects should contain **independent work, research, or applications built by the user**.  
  - E-commerce sites should contain **product listings, descriptions, and checkout flows**, even if not explicitly provided.  
- Do not mix up unrelated content.  

🔹 **3. Handle Missing Details Intelligently**  
- If a required section (e.g., "Products" for an e-commerce site) is missing, **generate logical placeholders** instead of leaving it blank.  
- If image placements are not specified, **position them naturally based on the content structure**.  

🔹 **4. Maintain User-Specified Constraints**  
- If the user provides complete details, **do not add extra information**.  
- Follow any specific requests **exactly as given** (e.g., if a user specifies exact sections, do not modify them).  

Return the response **only as a valid JSON object**, with no extra text.
"""

    try:
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a structured data generator. Your output must be valid JSON with standard array notation like [\"item1\", \"item2\"] for arrays. Do not use {\"0\": \"item1\", \"1\": \"item2\"} format for arrays."},
                {"role": "user", "content": structured_prompt}
            ],
            temperature=0.5,  # Lowered for more consistent results
            response_format={"type": "json_object"}  # Ensure JSON output
        )

        # Extract response content
        response_text = response.choices[0].message.content.strip()
        structured_data = json.loads(response_text)
        
        # 🔥 Fix: Define prompt_list before using it
        prompt_list = [p.strip() for p in image_prompts.split(",")] if image_prompts else []
        
        # 🔥 Ensure images are stored with correct placement
        structured_data["image_placements"] = []
        for i, img in enumerate(image_data):
            placement = prompt_list[i] if i < len(prompt_list) else "auto"
            structured_data["image_placements"].append({"path": img["path"], "placement": placement})

        return structured_data
    
    except Exception as e:
        return {"error": f"Failed to process input: {str(e)}"}