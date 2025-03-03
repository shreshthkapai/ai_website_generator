import subprocess
import os
import glob

# Replace these with your actual Node.js and npm paths or set them in your environment
NODE_PATH = "node"  # e.g., r"C:\Program Files\nodejs\node.exe" or just "node" if globally available
NPM_PATH = "npm"    # e.g., r"C:\Program Files\nodejs\npm.cmd" or just "npm" if globally available

def check_node_npm():
    try:
        node_version = subprocess.run([NODE_PATH, "--version"], capture_output=True, text=True)
        npm_version = subprocess.run([NPM_PATH, "--version"], capture_output=True, text=True)
        if node_version.returncode == 0 and npm_version.returncode == 0:
            print(f"✅ Node.js {node_version.stdout.strip()} and npm {npm_version.stdout.strip()} are installed.")
            return True
        else:
            print("❌ Node.js or npm is not installed.")
            return False
    except FileNotFoundError:
        print("❌ Node.js or npm is not installed.")
        return False

def find_vercel_executable():
    possible_locations = [
        subprocess.run([NPM_PATH, "bin", "-g"], capture_output=True, text=True).stdout.strip(),
        os.path.join(subprocess.run([NPM_PATH, "prefix", "-g"], capture_output=True, text=True).stdout.strip(), "node_modules", ".bin"),
        # Replace these with your environment-specific paths if needed
        os.path.join(os.environ.get("CONDA_PREFIX", ""), "Scripts"),  # For Anaconda environments
        os.path.join(os.environ.get("APPDATA", ""), "npm")           # For global npm installations
    ]
    
    print("\nSearching for Vercel executable in these locations:")
    for location in possible_locations:
        print(f"- {location}")
        
        for ext in [".cmd", ".exe", ".bat", ""]:
            path = os.path.join(location, f"vercel{ext}")
            if os.path.exists(path):
                print(f"\n✅ Found Vercel at: {path}")
                return path
    
    print("\n❌ Could not find Vercel executable in standard locations.")
    
    return None

def main():
    print("==== Vercel Deployment Setup ====\n")
    if not check_node_npm():
        print("\n⚠️ Please install Node.js and npm first, then run this script again.")
        return
    
    print("\nLocating Vercel CLI...")
    vercel_path = find_vercel_executable()
    
    if vercel_path:
        print(f"\n✅ Vercel CLI found at: {vercel_path}")
        
        try:
            version = subprocess.run([vercel_path, "--version"], capture_output=True, text=True)
            print(f"✅ Vercel CLI version: {version.stdout.strip()}")
            
            print("\nYou need to log in to Vercel to deploy websites.")
            choice = input("Do you want to log in now? (y/n): ")
            if choice.lower() in ["y", "yes"]:
                login_to_vercel(vercel_path)
            else:
                print("\n==== Setup Complete ====")
                print("You can now deploy websites using Vercel.")
                print(f"Use this path for Vercel in your scripts: {vercel_path}")
        except Exception as e:
            print(f"❌ Error testing Vercel: {e}")
    else:
        print("\n⚠️ Vercel CLI not found. Try reinstalling with:")
        print(f"{NPM_PATH} install -g vercel")

def login_to_vercel(vercel_path):
    try:
        print("\nLogging in to Vercel...")
        print("A browser window will open for authentication.")
        print("After logging in, return to this window to continue.")
        
        subprocess.run([vercel_path, "login"], check=True)
        
        print("✅ Logged in to Vercel successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error logging in to Vercel: {e}")
        return False
    except FileNotFoundError as e:
        print(f"❌ Could not find Vercel executable: {e}")
        return False

if __name__ == "__main__":
    main()