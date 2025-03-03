import os
import json
from openai import OpenAI
import re
import shutil
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")
openai = OpenAI(api_key=openai_api_key)

MODEL = "gpt-4o"

def validate_and_fix_website(structured_input, website_folder):
    possible_files = ['index.html', 'styles.css', 'script.js', 'seo.json', 'alpine.js', 'tailwind.config.js', 'postcss.config.js']
    
    if structured_input.get("website_structure") == "multi-page" and "pages" in structured_input:
        for page in structured_input["pages"]:
            page_filename = f"{page.lower().replace(' ', '-')}.html"
            if page_filename not in possible_files and page_filename != "index.html":
                possible_files.append(page_filename)
    
    website_files = {}
    any_files_exist = False
    for file_name in possible_files:
        file_path = os.path.join(website_folder, file_name)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
                if file_content.strip():
                    website_files[file_name] = file_content
                    any_files_exist = True

    if not any_files_exist:
        return {"error": "❌ No website files found to validate. Please check the website generation step."}

    validated_folder = website_folder + "_validated"
    os.makedirs(validated_folder, exist_ok=True)

    images_dir = os.path.join(website_folder, "images")
    validated_images_dir = os.path.join(validated_folder, "images")
    if os.path.exists(images_dir):
        if os.path.exists(validated_images_dir):
            shutil.rmtree(validated_images_dir)
        shutil.copytree(images_dir, validated_images_dir)
        print(f"✅ Copied images directory to {validated_images_dir}")

    for file_name, content in website_files.items():
        if file_name.endswith('.html'):
            html_content = content
            
            original_tags = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', html_content)
            print(f"Original image paths in {file_name}: {original_tags}")
            
            img_pattern = re.compile(r'<img[^>]*src="([^"]+)"')
            def img_replace(match):
                src = match.group(1)
                if src.startswith('C:') or src.startswith('/') or src.startswith('\\') or src.startswith('static'):
                    img_name = os.path.basename(src)
                    return match.group(0).replace(src, f"images/{img_name}")
                return match.group(0)
            
            html_content = img_pattern.sub(img_replace, html_content)
            
            img_class_pattern = re.compile(r'<img([^>]*)(?!class=)([^>]*)>')
            html_content = img_class_pattern.sub(r'<img\1 class="max-w-full h-auto object-cover"\2>', html_content)
            
            img_with_class_pattern = re.compile(r'<img([^>]*)class=["\'](.*?)["\']([^>]*)>')
            def class_replace(match):
                existing_class = match.group(2)
                if "max-w-full" not in existing_class and "h-auto" not in existing_class:
                    return f'<img{match.group(1)}class="{existing_class} max-w-full h-auto object-cover"{match.group(3)}>'
                return match.group(0)
            
            html_content = img_with_class_pattern.sub(class_replace, html_content)
            
            img_lazy_pattern = re.compile(r'<img([^>]*)(?!loading=)([^>]*)>')
            html_content = img_lazy_pattern.sub(r'<img\1 loading="lazy"\2>', html_content)
            
            fixed_tags = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', html_content)
            print(f"✅ Fixed image paths in {file_name}: {fixed_tags}")

            validated_html_path = os.path.join(validated_folder, file_name)
            with open(validated_html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"✅ Saved updated {file_name} to {validated_html_path}")

    validation_prompt = f"""You are a senior UI/UX designer and front-end architect with exceptional attention to detail. Your task is to review and enhance the provided website code to ensure it meets professional standards.

### **Structured Input (User Requirements):**
{json.dumps(structured_input, indent=2)}

### **Validation & Enhancement Tasks:**
1. **Technical Accuracy**: Fix any errors in HTML, CSS, and JavaScript.  
2. **Content Integrity**: Ensure all content from the structured input is properly displayed.  
3. **Styling**: Verify proper use of Tailwind CSS and fix any inconsistencies.  
4. **Responsiveness**: Ensure the website and all of its text is fully mobile-responsive and looks properly aligned and clean on all screen sizes.  
   - Check specifically for text overlay issues in the header and navigation
   - Ensure header text has proper responsive sizing, spacing, and alignment
   - Verify that header content properly collapses into the mobile menu on small screens
   - Fix any z-index issues that might cause header text to overlay improperly
5. **Animations & Interactions**: Enhance animations and interactions where appropriate.  
6. **Image Placement**: Ensure all images are responsive and properly sized.
   - Fix any image dimensions that may cause cutting or distortion
   - Ensure product images maintain proper aspect ratios
   - Implement proper lazy loading
7. **Theme Adherence**: Ensure the website follows the user-specified theme and aesthetics.  
8. **SEO & Accessibility**: Check for basic SEO and accessibility.  
9. **Multi-page Consistency**: If this is a multi-page website, ensure:
   - Consistent navigation across all pages
   - Proper internal links between pages
   - Consistent header and footer on all pages

### **Strict Rules**:  
- Do NOT add new pages that weren't in the original files.  
- Return the SAME files that were provided, with your improvements.  
- Maintain ALL the HTML files provided, don't convert to single page if multiple pages exist.

### **Output Format**:  
Return only a valid JSON object with the enhanced files.
"""

    try:
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a professional web developer. Your ONLY job is to fix existing website code. Return ONLY a valid JSON object with the fixed files, nothing else."},
                {"role": "user", "content": validation_prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        response_text = response.choices[0].message.content.strip()
        
        try:
            fixed_files = json.loads(response_text)
            
            if "index.html" in fixed_files and ("UI/UX Excellence" in fixed_files["index.html"] or 
                                               "Design Guide" in fixed_files["index.html"]):
                return {"error": "❌ Validation failed: Model returned a UI/UX guide instead of the expected website."}
                
            for file_name, content in fixed_files.items():
                if content and content.strip():
                    file_path = os.path.join(validated_folder, file_name)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
            
            return {
                "message": "✅ Website validated and fixed successfully!", 
                "validated_folder": validated_folder, 
                "fixed_files": [k for k, v in fixed_files.items() if v and v.strip()]
            }
        except json.JSONDecodeError as e:
            return {"error": f"❌ Validation failed: Invalid JSON response: {str(e)}"}
    
    except Exception as e:
        import traceback
        return {
            "error": f"❌ Validation failed: {str(e)}",
            "traceback": traceback.format_exc()
        }