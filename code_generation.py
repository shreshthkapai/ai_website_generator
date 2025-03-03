from openai import OpenAI
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")
openai = OpenAI(api_key=openai_api_key)

MODEL = "gpt-4o"

def generate_website_code(structured_data):
    system_prompt = """You are an elite senior full-stack developer specializing in modern, responsive, and visually stunning websites. Use **HTML, Tailwind CSS, Vanilla JS, and Alpine.js (if needed)**. Follow these guidelines:

1. **Tech Stack**:  
   - Use **Tailwind CSS** for styling. Avoid Bootstrap or excessive inline styles.  
   - Use **Vanilla JS** or **Alpine.js** for interactivity if required.  

2. **User Requests**:  
   - Strictly adhere to the user's prompts and structured data.  
   - If the user requests specific features (e.g., animations, themes, layouts, SEO), implement them precisely.  

3. **Footer Content**:  
   - If the user provides footer content, include it exactly as specified.  
   - If no footer content is provided, omit the footer.  

4. **SEO Optimization**:  
   - Include basic SEO best practices by default:  
     - Add a `<title>` tag based on the website's purpose.  
     - Include `<meta>` tags for description and keywords (if provided).  
     - Use semantic HTML tags (e.g., `<header>`, `<main>`, `<section>`, `<footer>`).  
     - Add `alt` attributes to images.  
   - If the user provides specific SEO requirements, prioritize those.  
   - Add Open Graph tags for social media sharing (e.g., `og:title`, `og:description`, `og:image`).  
   - Include schema markup for better search engine visibility (e.g., `Person` schema for a portfolio).  

5. **Creative Freedom**:  
   - If essential details are missing, use your expertise to fill gaps while maintaining a professional and modern design and text styles and fonts.  

"6. **Output Format**:  
     - Return a **valid JSON object** with these keys:  
     - `index.html`: Complete HTML file for the home/landing page.
     - Additional HTML files for multi-page websites (e.g., `products.html`, `contact.html`).
     - `styles.css`: Custom CSS (if not inline).  
     - `script.js`: JavaScript code.
     - `tailwind.config.js`: Tailwind config (if needed).  
     - `postcss.config.js`: PostCSS config (if needed).  
   - Do not include explanations or markdown. 

7. **Image Handling**:  
   - Use relative paths for image references in the HTML as `src="images/<filename>"`, regardless of the input path provided.  
   - Ensure all images are referenced correctly in the `images/` folder.

8. **Mobile Responsiveness**:  
   - Implement a hamburger menu for the navigation bar on smaller screens.  
   - Use Tailwind CSS or custom JavaScript to toggle the menu visibility.  
   - Make sure the website is fully responsive and looks clean and proper on all screen sizes.
   - Make sure the header and all its text and elements are perfectly aligned and responsive for all screen sizes.
   - Ensure all header text uses responsive font sizing (e.g., text-base md:text-lg lg:text-xl)
   - Implement proper text wrapping or truncation for navigation items on small screens
   - Verify that text containers have appropriate padding/margin that scales with screen size
   - Add sufficient spacing between header elements to prevent text overlap on mobile screens

9. **Animations**:  
    - Add subtle fade-in animations for sections using Tailwind CSS or JavaScript.  
    - Ensure animations are smooth and do not affect performance.  

10. **Website Structure**:
    - If the structured data indicates a multi-page website ("website_structure": "multi-page"), create multiple HTML files.
    - Generate a separate HTML file for each page listed in the "pages" array.
    - Create consistent navigation between all pages.
    - Each page should have the same header and footer for consistency.
    - Name the primary HTML file "index.html" (home page) and other pages as "[page-name].html".
    - If website structure is not present you have freedom to make it either multi page or single page depending on the prompt.
"""

    # Preprocess structured_data to force images/ paths
    modified_structured_data = structured_data.copy()
    if "image_placements" in modified_structured_data:
        for img in modified_structured_data["image_placements"]:
            if "path" in img:
                img_name = os.path.basename(img["path"])
                img["path"] = f"images/{img_name}"  # Force images/ here

    user_prompt = f"""
Generate a senior-dev-level website based on the following input. Follow the user's requests strictly and use your expertise to fill any gaps creatively.

### Input Data:  
- **Theme**: {modified_structured_data.get('websiteTheme', 'Default Modern Theme')}  
- **Images**: {modified_structured_data.get('images', 'No images provided')}  
- **Content**: {json.dumps(modified_structured_data, indent=2)}  

Return the response as a valid JSON object with the required keys.  
"""

    try:
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.6,
            response_format={"type": "json_object"}
        )

        raw_content = response.choices[0].message.content.strip()
        raw_content = re.sub(r"^```json|```$", "", raw_content).strip()

        try:
            generated_code = json.loads(raw_content)
            return generated_code
        except json.JSONDecodeError:
            print(f"Failed to parse JSON. Raw response: {raw_content}")
            return {"error": "Failed to generate valid website code."}
    except Exception as e:
        print(f"Error in generate_website_code: {e}")
        return {"error": f"Error generating website code: {e}"}