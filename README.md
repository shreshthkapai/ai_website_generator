# AI Website Generator
Effortlessly generate fully functional websites with text and image uploads. This AI-powered system automates everything from generating the website to deploying it on Vercel.


## Features:
1. Gradio Interface: Enter a prompt and upload images (you can give prompts for each image u upload as well; if you upload multiple images, separate each image prompt with a ',') with ease.
2. AI-Powered Code Generation: Uses the OpenAI 4o model to dynamically create structured, SEO-optimized code.
3. Automated Validation: Ensures the generated code aligns with the prompt.
4. One-Click Deployment: Instantly deploys to Vercel with no manual setup.
5. Pre-Processes Input: Converts input into valid JSON for structured processing.
6. Smart Image Handling: AI infers image roles dynamically, with no manual resizing required. (Although this feature is not completely robust as of now.)
7. Supports Various Website Types: Personal, landing pages, e-commerce, and more (It supports both multi page and single page websites and supports varying screen sizes)!


## How it works:
1. Provide a prompt, enter your website domain name (optional), upload images you want in your website, and prompt where you want them (optional).
2. OpenAI 4o model preprocesses the input into valid JSON.
3. This generated JSON is again fed into the 4o model to generate and validate the website code.
4. The website is automatically deployed to Vercel.
5. Access your fully functional site instantly!

⏳ Full deployment from the prompt takes approximately 3 minutes.

## Live Demos
Check out some AI-generated websites deployed using this project:
1. [Beachy Clothes](beachy-clothes-jy4zz1auq-shreshth-kapais-projects.vercel.app) (Multipage website, the images were uploaded via image prompt, I know that the image sizing may be messed up. Still trying to improve it :/). 
2.  [Personal Website](https://beachy-clothes--ten.vercel.app/) (Single Page website, my image was uploaded via image prompt)

##  Ongoing Work & Improvements
Looking for contributors to help with the following:
1. More robust image sizing based on the image prompt—if you have experience, we’d love your input!
2. Prompt engineers who can craft better full-stack-based prompts for generating higher-quality websites.

## Contributing
Feel free to submit issues and pull requests to enhance the project.
