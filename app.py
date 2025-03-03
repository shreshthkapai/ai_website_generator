import gradio as gr
import shutil
import time
import os
from input_processing import process_user_input
from code_generation import generate_website_code
from save_website_code_files import save_generated_website
from validate_generated_code import validate_and_fix_website
from vercel_deployment import deploy_to_vercel

# Use a relative path instead of absolute path
UPLOAD_FOLDER = os.path.join("static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def handle_input(prompt, images, image_prompts, website_name, progress=gr.Progress()):
    image_data = []

    progress(0, desc="Processing input...")
    
    if images:
        prompt_list = [p.strip() for p in image_prompts.split(",")] if image_prompts else []

        for i, img in enumerate(images):
            original_name = os.path.basename(img.name if hasattr(img, 'name') else img)
            name, ext = os.path.splitext(original_name)
            unique_name = f"{name}_{int(time.time()*1000)}{ext}"  # e.g., upper_1634567890123.jpeg
            img_path = os.path.join(UPLOAD_FOLDER, unique_name)

            if isinstance(img, str):
                if os.path.abspath(img) != os.path.abspath(img_path):
                    shutil.copy(img, img_path)
                    print(f"Copied image from {img} to {img_path}")
            else:
                img.save(img_path)
                print(f"Saved image to {img_path}")

            img_prompt = prompt_list[i] if i < len(prompt_list) else "auto"
            image_data.append({"path": img_path, "placement": img_prompt})

    # Processing input
    structured_input = process_user_input(prompt, image_data, image_prompts)
    if "error" in structured_input:
        return {"error": structured_input["error"]}
    
    # Generating code
    progress(0.25, desc="Generating website code...")
    generated_code = generate_website_code(structured_input)
    if "error" in generated_code:
        return {"error": generated_code["error"]}

    # Saving website files
    progress(0.5, desc="Saving website files...")
    website_folder = save_generated_website(generated_code, image_data)
    if not website_folder:
        return {"error": "❌ Website generation failed. Please try again."}

    # Validating website
    progress(0.75, desc="Validating website...")
    validation_result = validate_and_fix_website(structured_input, website_folder)
    if "error" in validation_result:
        return {"error": validation_result["error"]}

    validated_folder = validation_result.get("validated_folder", website_folder)
    
    # Deploying to Vercel
    progress(0.9, desc="Deploying to Vercel...")
    deployment_result = deploy_to_vercel(validated_folder, website_name)

    if "error" in deployment_result:
        return {
            "error": deployment_result["error"], 
            "local_folder": validated_folder
        }

    progress(1.0, desc="Website deployed! 🚀")
    deployment_url = deployment_result.get("url", "URL not available")
    
    return {
        "message": "✅ Website generated, validated, and deployed successfully!",
        "deployment_url": deployment_url,   
        "local_folder": validated_folder,
        "project_name": deployment_result.get("project_name", "")
    }

with gr.Blocks() as ui:
    gr.Markdown("# 🚀 AI Website Generator")

    with gr.Row():
        prompt = gr.Textbox(
            label="Enter your website description", 
            lines=4, 
            placeholder="e.g., A personal website for an AI Engineer.",
            elem_id="prompt-input"
        )

    with gr.Row():
        website_name = gr.Textbox(
            label="Website Name (optional)", 
            placeholder="my-awesome-website",
            elem_id="website-name-input"
        )

    with gr.Row():
        images = gr.Files(
            file_types=["image"], 
            label="Upload Images", 
            interactive=True,
            elem_id="image-upload"
        )

    with gr.Row():
        image_prompts = gr.Textbox(
            label="Describe Image Placement (comma-separated)", 
            placeholder="e.g., Hero section, About page, Footer",
            elem_id="image-prompts-input"
        )

    with gr.Row():
        submit = gr.Button(
            "Generate & Deploy Website", 
            variant="primary",
            elem_id="submit-button"
        )

    with gr.Row():
        output = gr.JSON(
            label="Result",
            elem_id="output-json"
        )

    submit.click(
        handle_input, 
        inputs=[prompt, images, image_prompts, website_name], 
        outputs=output
    )

ui.launch()