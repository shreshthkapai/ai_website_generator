import os
import json
import shutil
import re

# Use a relative path instead of absolute path
GENERATED_WEBSITES_DIR = os.path.join("generated_websites")

def fix_image_paths_in_html(html_content, images):
    print(f"Fixing image paths in HTML...")
    img_tags = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', html_content)
    print(f"Before fixing: {img_tags}")
    
    for img in images:
        if isinstance(img, dict) and "path" in img:
            img_name = os.path.basename(img["path"])
            html_content = html_content.replace(img["path"], f"images/{img_name}")
            html_content = html_content.replace(f"static/{img_name}", f"images/{img_name}")
            html_content = html_content.replace(f"static\\{img_name}", f"images/{img_name}")
            html_content = html_content.replace(f"static/{img_name.replace(' ', '%20')}", f"images/{img_name}")
    
    # Forcefully replace any static/ with images/
    html_content = re.sub(
        r'<img[^>]+src=[\'"]static[/\\]([^\'"]+)[\'"]',
        r'<img src="images/\1"',
        html_content
    )
    
    img_tags_after = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', html_content)
    print(f"After fixing: {img_tags_after}")
    return html_content

def get_next_folder_name():
    """Generates a unique folder name like website_001, website_002, etc."""
    if not os.path.exists(GENERATED_WEBSITES_DIR):
        os.makedirs(GENERATED_WEBSITES_DIR)

    existing_folders = [f for f in os.listdir(GENERATED_WEBSITES_DIR) if f.startswith("website_")]
    existing_numbers = sorted([int(f.split("_")[1]) for f in existing_folders if f.split("_")[1].isdigit()])

    next_number = existing_numbers[-1] + 1 if existing_numbers else 1
    return f"website_{str(next_number).zfill(3)}"

def save_generated_website(website_json, images):
    website_folder = os.path.join(GENERATED_WEBSITES_DIR, get_next_folder_name())
    os.makedirs(website_folder, exist_ok=True)

    try:
        website_data = json.loads(website_json) if isinstance(website_json, str) else website_json
        print(f"📂 Saving files to: {website_folder}")

        file_mapping = {
            "index.html": "index.html",
            "styles.css": "styles.css",
            "script.js": "script.js",
            "alpine.js": "alpine.js",
            "seo.json": "seo.json",
            "tailwind.config.js": "tailwind.config.js",
            "postcss.config.js": "postcss.config.js"
        }

        for key, filename in file_mapping.items():
            if key in website_data and website_data[key]:
                file_path = os.path.join(website_folder, filename)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(website_data[key])
                print(f"✅ Saved {filename}")

        images_dir = os.path.join(website_folder, "images")
        os.makedirs(images_dir, exist_ok=True)
        
        if "index.html" in website_data:
            html_content = website_data["index.html"]
            if isinstance(images, list):
                for img in images:
                    if isinstance(img, dict) and "path" in img:
                        img_name = os.path.basename(img["path"])
                        img_dest_path = os.path.join(images_dir, img_name)
                        shutil.copy(img["path"], img_dest_path)
                        print(f"🖼️ Copied image: {img_name} to {img_dest_path}")
            
            # Fix image paths
            html_content = fix_image_paths_in_html(html_content, images)
            
            # Add favicon handling (optional)
            if not os.path.exists(os.path.join(images_dir, "favicon.ico")):
                # Specify a default favicon path in your project directory
                default_favicon = os.path.join("assets", "default_favicon.ico")  # Update this path in your project
                if os.path.exists(default_favicon):
                    shutil.copy(default_favicon, os.path.join(images_dir, "favicon.ico"))
                    print(f"✅ Copied default favicon to {images_dir}")
                    html_content = html_content.replace('</head>', '<link rel="icon" href="images/favicon.ico">\n</head>')
                else:
                    print("⚠️ No default favicon found at specified path; skipping favicon addition.")

            # Save the updated HTML
            file_path = os.path.join(website_folder, "index.html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"✅ Updated and saved index.html with fixed image paths and favicon")

        print(f"🎉 Website saved successfully in {website_folder}")
        return website_folder

    except Exception as e:
        print(f"❌ Error saving website: {e}")
        return None