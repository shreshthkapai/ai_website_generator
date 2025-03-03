import os
import json
import subprocess
import shutil
import time
from pathlib import Path
import uuid
import re

def prepare_for_vercel(website_folder, custom_name=None):
    print(f"Preparing {website_folder} for Vercel deployment...")

    if custom_name and custom_name.strip():
        project_name = "".join(c if c.isalnum() or c == '-' else '-' for c in custom_name.strip().lower())
        if not project_name[0].isalpha():
            project_name = f"web-{project_name}"
        project_name = project_name[:40]
    else:
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]
        project_name = f"ai-website-{timestamp}-{unique_id}"

    vercel_config = {
        "name": project_name,
        "version": 2,
        "public": True,  
        "builds": [
            {"src": "*.html", "use": "@vercel/static"},
            {"src": "*.css", "use": "@vercel/static"},
            {"src": "*.js", "use": "@vercel/static"},
            {"src": "*.json", "use": "@vercel/static"},
            {"src": "images/**", "use": "@vercel/static"}
        ],
        "routes": [
            {"src": "/images/(.*)", "dest": "/images/$1"},
            {"src": "/(.*)", "dest": "/$1"},
            {"handle": "filesystem"},
            {"src": "/", "dest": "/index.html"}
        ]
    }

    vercel_json_path = os.path.join(website_folder, "vercel.json")
    with open(vercel_json_path, "w", encoding="utf-8") as f:
        json.dump(vercel_config, f, indent=2)

    package_json = {
        "name": project_name,
        "version": "0.0.1",
        "scripts": {
            "start": "serve"
        },
        "dependencies": {
            "serve": "^14.0.0"
        }
    }

    package_json_path = os.path.join(website_folder, "package.json")
    with open(package_json_path, "w", encoding="utf-8") as f:
        json.dump(package_json, f, indent=2)

    print(f"✅ Vercel deployment files created successfully in {website_folder}")
    print(f"Checking directory structure before deployment:")
    
    for root, dirs, files in os.walk(website_folder):
        rel_path = os.path.relpath(root, website_folder)
        if rel_path == '.':
            for file in files:
                print(f"Root file: {file}")
        else:
            for file in files:
                print(f"Subfolder file: {rel_path}/{file}")
                
    images_dir = os.path.join(website_folder, "images")
    if os.path.exists(images_dir):
        image_files = os.listdir(images_dir)
        print(f"Found {len(image_files)} images in the images directory:")
        for img in image_files:
            print(f" - images/{img}")
    else:
        print("⚠️ WARNING: No 'images' directory found!")
        
    return project_name

def deploy_to_vercel(website_folder, custom_name=None):
    try:
        if not os.path.exists(website_folder):
            return {"error": f"Website folder {website_folder} does not exist"}

        project_name = prepare_for_vercel(website_folder, custom_name if custom_name else None)

        original_dir = os.getcwd()
        os.chdir(website_folder)

        print(f"🚀 Deploying {project_name} to Vercel...")

        # Replace with the correct path to your Vercel CLI or ensure it's globally available
        vercel_path = "vercel"  # e.g., r"C:\Users\YourUser\AppData\Roaming\npm\vercel.cmd"
        result = subprocess.run([vercel_path, "--prod", "--yes"], capture_output=True, text=True, check=True)

        os.chdir(original_dir)

        output_lines = result.stdout.split("\n")
        deployment_url = None

        for line in output_lines:
            if "https://" in line and "vercel.app" in line:
                deployment_url = line.strip()
                break

        if not deployment_url:
            url_pattern = r'https://[\w.-]+vercel\.app'
            matches = re.findall(url_pattern, result.stdout)
            if matches:
                deployment_url = matches[0]

        if deployment_url:
            print(f"✅ Website deployed successfully to: {deployment_url}")
            return {
                "status": "success",
                "message": "Website deployed successfully!",
                "url": deployment_url,
                "project_name": project_name
            }
        else:
            print(f"⚠️ Deployment seems successful but couldn't extract URL.")
            print(f"Vercel output: {result.stdout}")
            return {
                "status": "partial_success",
                "message": "Deployment completed but couldn't extract URL",
                "vercel_output": result.stdout,
                "project_name": project_name
            }

    except subprocess.CalledProcessError as e:
        print(f"❌ Vercel deployment failed: {e}")
        print(f"Error output: {e.stderr}")

        if "command not found" in e.stderr or "not recognized" in e.stderr:
            return {
                "error": "Vercel CLI is not installed. Please run 'npm i -g vercel' to install it."
            }
        elif "not logged in" in e.stderr:
            return {
                "error": "Vercel is not authenticated. Please run 'vercel login' to authenticate."
            }
        else:
            return {        
                "error": f"Deployment failed: {e.stderr}"
            }
    except Exception as e:
        print(f"❌ Error during deployment: {str(e)}")
        return {
            "error": f"Deployment failed: {str(e)}"
        }
    finally:
        if 'original_dir' in locals():
            os.chdir(original_dir)