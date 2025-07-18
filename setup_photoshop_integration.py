import os
import subprocess
import requests
import platform
import sys
import zipfile
import shutil
from tqdm import tqdm
import argparse

# --- Configuration ---

# Paths
COMFYUI_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
CUSTOM_NODES_DIR = os.path.join(COMFYUI_ROOT, "custom_nodes")
MODELS_DIR = os.path.join(COMFYUI_ROOT, "models")
PLUGIN_FILE = os.path.join(CUSTOM_NODES_DIR, "comfyui-photoshop", "Install_Plugin", "3e6d64e0_PS.zip")

# Git Repositories for Custom Nodes
CUSTOM_NODE_REPOS = {
    "comfyui-photoshop": "https://github.com/NimaNzrii/comfyui-photoshop.git",
    "comfy_mtb": "https://github.com/melMass/comfy_mtb.git",
    "rgthree-comfy": "https://github.com/rgthree/rgthree-comfy.git",
    "cg-use-everywhere": "https://github.com/chrisgoringe/cg-use-everywhere.git",
    "ComfyUI-Advanced-ControlNet": "https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet.git",
    "comfyui_controlnet_aux": "https://github.com/Fannovel16/comfyui_controlnet_aux.git",
    "ComfyUI_essentials": "https://github.com/cubiq/ComfyUI_essentials.git",
}

# SD-PPP Repository
SD_PPP_REPO = "https://github.com/zombieyang/sd-ppp.git"

# Model URLs and their destinations
MODELS_TO_DOWNLOAD = {
    "checkpoints": {
        "epicrealism_naturalSinRC1VAE.safetensors": "https://huggingface.co/philz1337x/epicrealism/resolve/main/epicrealism_naturalSinRC1VAE.safetensors",
        "epicrealism_pureEvolutionV5-inpainting.safetensors": "https://huggingface.co/phoenix-1708/DR_NED/resolve/main/epicrealism_pureEvolutionV5-inpainting.safetensors",
    },
    "loras": {
        "LCM_LoRA_SD1.5.safetensors": "https://huggingface.co/latent-consistency/lcm-lora-sdv1-5/resolve/main/pytorch_lora_weights.safetensors",
        "add_detail.safetensors": "https://civitai.com/api/download/models/62833",
    },
    "controlnet": {
        "control_v11p_sd15_lineart_fp16.safetensors": "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_v11p_sd15_lineart_fp16.safetensors",
        "control_v11p_sd15_scribble_fp16.safetensors": "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_v11p_sd15_scribble_fp16.safetensors",
        "control_v11p_sd15_inpaint_fp16.safetensors": "https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_v11p_sd15_inpaint_fp16.safetensors",
    },
    "upscale_models": {
        "4x-UltraSharp.pth": "https://huggingface.co/lokCX/4x-Ultrasharp/resolve/main/4x-UltraSharp.pth",
    },
}

# --- Helper Functions ---

def print_header(title):
    print("\n" + "="*50)
    print(f"    {title}")
    print("="*50)

def check_and_install_zxp_installer():
    print_header("1. Checking for ZXP Installer")
    try:
        # Check if ZXP Installer is already installed via Homebrew
        result = subprocess.run(["brew", "list", "--cask", "zxpinstaller"], capture_output=True, text=True)
        if result.returncode == 0 and "zxpinstaller" in result.stdout:
            print("✅ ZXP Installer is already installed via Homebrew.")
            return True

        # If not found, try to install it
        print("   ZXP Installer not found. Attempting to install via Homebrew...")
        install_result = subprocess.run(["brew", "install", "--cask", "zxpinstaller"], check=True)
        print("✅ ZXP Installer installed successfully.")

        # Remind Apple Silicon users about Rosetta 2
        if platform.processor() == "arm":
            print("\n   NOTE FOR APPLE SILICON (M1/M2/M3/M4) USERS:")
            print("   ZXP Installer may require Rosetta 2 to run.")
            print("   If it fails to launch, run this command in your terminal:")
            print("   softwareupdate --install-rosetta --agree-to-license")

        return True

    except FileNotFoundError:
        print("❌ ERROR: Homebrew is not installed or not in your PATH.")
        print("   Please install Homebrew first: https://brew.sh/")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: Failed to install ZXP Installer. Brew command failed: {e}")
        return False


def install_custom_nodes():
    print_header("2. Installing Custom Nodes")
    os.makedirs(CUSTOM_NODES_DIR, exist_ok=True)
    for name, url in CUSTOM_NODE_REPOS.items():
        repo_path = os.path.join(CUSTOM_NODES_DIR, name)
        if os.path.exists(repo_path):
            print(f"   Updating {name}...")
            # Use --force to avoid conflicts with local changes
            subprocess.run(["git", "pull", "--force"], cwd=repo_path, check=True)
        else:
            print(f"   Cloning {name}...")
            subprocess.run(["git", "clone", url, repo_path], check=True)
    print("✅ All custom nodes installed/updated.")

def download_file(url, dest_path, file_name):
    if os.path.exists(dest_path):
        print(f"   - {file_name} already exists. Skipping.")
        return

    try:
        # Add a user-agent to handle sites like Civitai
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        with requests.get(url, stream=True, allow_redirects=True, headers=headers) as r:
            # For Civitai, the filename is in the headers
            if 'civitai.com' in url:
                content_disposition = r.headers.get('content-disposition')
                if content_disposition:
                    filename_in_header = content_disposition.split('filename=')[-1].strip('"')
                    dest_path = os.path.join(os.path.dirname(dest_path), filename_in_header)
                    file_name = filename_in_header
                    if os.path.exists(dest_path):
                         print(f"   - {file_name} already exists. Skipping.")
                         return


            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            with open(dest_path, 'wb') as f, tqdm(
                desc=file_name,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in r.iter_content(chunk_size=8192):
                    size = f.write(chunk)
                    bar.update(size)
        print(f"   ✅ Downloaded {file_name}")
    except Exception as e:
        print(f"   ❌ ERROR downloading {file_name}: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path)


def install_custom_node_dependencies():
    print_header("3. Installing Custom Node Dependencies")
    for item in os.listdir(CUSTOM_NODES_DIR):
        node_path = os.path.join(CUSTOM_NODES_DIR, item)
        requirements_path = os.path.join(node_path, "requirements.txt")
        if os.path.isdir(node_path) and os.path.exists(requirements_path):
            print(f"   Installing dependencies for {item}...")
            try:
                with open(requirements_path, 'r') as f:
                    dependencies = f.readlines()

                processed_dependencies = []
                for dep in dependencies:
                    dep = dep.strip()
                    if not dep or dep.startswith('#'):
                        continue
                    if "onnxruntime-gpu" in dep:
                        print(f"      -> Replacing 'onnxruntime-gpu' with 'onnxruntime' for {item}")
                        processed_dependencies.append("onnxruntime")
                    else:
                        processed_dependencies.append(dep)

                if not processed_dependencies:
                    print(f"   No active dependencies found in {item}/requirements.txt. Skipping.")
                    continue

                # Install dependencies one by one to handle mediapipe gracefully
                for dep in processed_dependencies:
                    if "mediapipe" in dep:
                        print(f"      -> Attempting to install 'mediapipe' for {item} (may fail on some systems/Python versions)...\n")
                        try:
                            subprocess.run([os.path.join(os.path.dirname(sys.executable), "pip"), "install", dep], check=True)
                            print(f"      ✅ Successfully installed {dep}")
                        except subprocess.CalledProcessError as e:
                            print(f"      ⚠️ WARNING: Failed to install {dep} for {item}. This might be due to compatibility issues on your system/Python version.")
                            print(f"         STDOUT: {e.stdout}")
                            print(f"         STDERR: {e.stderr}")
                            print(f"         You may need to manually install or find a compatible version for {dep}.")
                    else:
                        subprocess.run([os.path.join(os.path.dirname(sys.executable), "pip"), "install", dep], check=True)

                print(f"   ✅ Dependencies for {item} installed.")
            except subprocess.CalledProcessError as e:
                print(f"   ❌ ERROR installing dependencies for {item}: {e}")
                print(f"      STDOUT: {e.stdout}")
                print(f"      STDERR: {e.stderr}")
            except FileNotFoundError:
                print(f"   ❌ ERROR: pip command not found. Ensure virtual environment is activated.")
        else:
            # print(f"   No requirements.txt found for {item}. Skipping.")
            pass
    print("\n✅ All custom node dependencies checked/installed.")

def download_models():
    print_header("4. Downloading Required Models")
    for model_type, models in MODELS_TO_DOWNLOAD.items():
        print(f"\n-> Checking {model_type} models...")
        dest_dir = os.path.join(MODELS_DIR, model_type)
        os.makedirs(dest_dir, exist_ok=True)
        for name, url in models.items():
            dest_path = os.path.join(dest_dir, name)
            download_file(url, dest_path, name)
    print("\n✅ All models checked/downloaded.")

def install_photoshop_plugin_manually():
    print_header("5. Installing Photoshop Plugin (Manual Copy)")
    
    # Define potential Photoshop plugin installation paths
    # Note: These paths are for macOS. For Windows, they would be different.
    # The user found these paths to be effective.
    photoshop_plugin_paths = [
        "/Library/Application Support/Adobe/CEP/extensions",  # System-level CEP extensions
        os.path.expanduser("~/Library/Application Support/Adobe/CEP/extensions"), # User-level CEP extensions
        "/Applications/Adobe Photoshop 2025/Plug-ins" # Photoshop application-level plugins
    ]

    temp_extract_dir = os.path.join(COMFYUI_ROOT, "temp_plugin_extract")
    
    try:
        # 1. Extract the .ccx file (treat as a zip)
        print(f"   Extracting plugin from: {PLUGIN_FILE}...")
        with zipfile.ZipFile(PLUGIN_FILE, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_dir)
        print(f"   ✅ Plugin extracted to: {temp_extract_dir}")

        # 2. Find the actual plugin folder within the extracted content
        # Based on user's manual inspection, the plugin content is directly in the extracted folder
        # Based on user's manual inspection, the plugin content is directly in the extracted folder
        plugin_content_dir = temp_extract_dir
        plugin_folder_name = "3e6d64e0_PS"

        # Verify if manifest.json exists in the assumed plugin content directory
        if not os.path.exists(os.path.join(plugin_content_dir, "manifest.json")):
            print("   ❌ ERROR: Could not find 'manifest.json' in the extracted plugin content. The plugin structure might be different than expected.")
            return

        # If the plugin folder is nested, find it
        nested_plugin_folder = None
        for item in os.listdir(temp_extract_dir):
            item_path = os.path.join(temp_extract_dir, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "manifest.json")):
                nested_plugin_folder = item_path
                plugin_folder_name = item # Update plugin_folder_name to the actual folder name
                break
        
        if nested_plugin_folder:
            plugin_content_dir = nested_plugin_folder
            print(f"   Found nested plugin folder: {plugin_folder_name}")
        else:
            print("   Using top-level extracted folder as plugin content.")

        print(f"   Identified plugin folder: {plugin_folder_name}")

        # 3. Copy the plugin folder to all potential Photoshop plugin paths
        for dest_path in photoshop_plugin_paths:
            target_plugin_path = os.path.join(dest_path, plugin_folder_name)
            print(f"   Attempting to copy plugin to: {target_plugin_path}...")
            
            try:
                # Ensure parent directories exist
                os.makedirs(dest_path, exist_ok=True)
                
                if os.path.exists(target_plugin_path):
                    print(f"   - Existing plugin found at {target_plugin_path}. Removing before copying.")
                    shutil.rmtree(target_plugin_path) # Remove existing to ensure fresh copy

                shutil.copytree(plugin_content_dir, target_plugin_path)
                print(f"   ✅ Successfully copied plugin to: {target_plugin_path}")
            except PermissionError:
                print(f"   ⚠️ WARNING: Permission denied to copy to {target_plugin_path}. You may need to run this script with administrator privileges (sudo).")
            except Exception as e:
                print(f"   ❌ ERROR copying plugin to {target_plugin_path}: {e}")

    except FileNotFoundError:
        print(f"   ❌ ERROR: Plugin file not found at {PLUGIN_FILE}. Please ensure it exists.")
    except zipfile.BadZipFile:
        print(f"   ❌ ERROR: The plugin file {PLUGIN_FILE} is not a valid zip file.")
    except Exception as e:
        print(f"   ❌ An unexpected error occurred during plugin installation: {e}")
    finally:
        # Clean up temporary extraction directory
        if os.path.exists(temp_extract_dir):
            print(f"   Cleaning up temporary directory: {temp_extract_dir}")
            shutil.rmtree(temp_extract_dir) # Re-enable cleanup after debugging

def uninstall_photoshop_integration(keep_models=False, uninstall_zxp=False):
    print_header("Uninstalling Photoshop Plugin and ComfyUI Integration")

    # Define potential Photoshop plugin installation paths
    photoshop_plugin_paths = [
        "/Library/Application Support/Adobe/CEP/extensions",  # System-level CEP extensions
        os.path.expanduser("~/Library/Application Support/Adobe/CEP/extensions"), # User-level CEP extensions
        "/Applications/Adobe Photoshop 2025/Plug-ins" # Photoshop application-level plugins
    ]
    
    plugin_folder_name = "3e6d64e0_PS" # The name of the folder copied to Photoshop

    # 1. Remove Photoshop plugin files
    print("\n-> Removing Photoshop plugin files...")
    for dest_path in photoshop_plugin_paths:
        target_plugin_path = os.path.join(dest_path, plugin_folder_name);
        if os.path.exists(target_plugin_path):
            try:
                shutil.rmtree(target_plugin_path)
                print(f"   ✅ Successfully removed plugin from: {target_plugin_path}")
            except PermissionError:
                print(f"   ⚠️ WARNING: Permission denied to remove from {target_plugin_path}. You may need to run this script with administrator privileges (sudo).")
            except Exception as e:
                print(f"   ❌ ERROR removing plugin from {target_plugin_path}: {e}")
        else:
            print(f"   - Plugin not found at: {target_plugin_path}. Skipping.")

    # 2. Remove comfyui-photoshop custom node
    print("\n-> Removing comfyui-photoshop custom node...")
    comfyui_photoshop_node_path = os.path.join(CUSTOM_NODES_DIR, "comfyui-photoshop")
    if os.path.exists(comfyui_photoshop_node_path):
        try:
            shutil.rmtree(comfyui_photoshop_node_path)
            print(f"   ✅ Successfully removed custom node: {comfyui_photoshop_node_path}")
        except Exception as e:
            print(f"   ❌ ERROR removing custom node {comfyui_photoshop_node_path}: {e}")
    else:
        print(f"   - Custom node not found at: {comfyui_photoshop_node_path}. Skipping.")

    # 3. Conditionally remove models
    if not keep_models:
        print("\n-> Removing downloaded models and LoRAs...")
        for model_type in MODELS_TO_DOWNLOAD.keys():
            model_dir = os.path.join(MODELS_DIR, model_type)
            if os.path.exists(model_dir):
                try:
                    shutil.rmtree(model_dir)
                    print(f"   ✅ Successfully removed model directory: {model_dir}")
                except Exception as e:
                    print(f"   ❌ ERROR removing model directory {model_dir}: {e}")
            else:
                print(f"   - Model directory not found: {model_dir}. Skipping.")
    else:
        print("\n-> Keeping downloaded models and LoRAs as requested.")

    # 4. Conditionally uninstall ZXP Installer
    if uninstall_zxp:
        print("\n-> Uninstalling ZXP Installer...")
        try:
            subprocess.run(["brew", "uninstall", "--cask", "zxpinstaller"], check=True)
            print("   ✅ ZXP Installer uninstalled successfully.")
        except FileNotFoundError:
            print("   ❌ ERROR: Homebrew is not installed or not in your PATH. Cannot uninstall ZXP Installer.")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ ERROR: Failed to uninstall ZXP Installer. Brew command failed: {e}")
    else:
        print("\n-> Keeping ZXP Installer as requested.")

    print("\n🎉 Uninstallation Complete!")
    print("Please remember to restart Photoshop and ComfyUI to ensure all changes take effect.")

def install_sdppp_plugin():
    print_header("Installing SD-PPP Plugin")

    sdppp_repo_path = os.path.join(CUSTOM_NODES_DIR, "sd-ppp")
    sdppp_plugin_source_path = os.path.join(sdppp_repo_path, "plugins", "photoshop")
    plugin_folder_name = "SD-PPP" # The name of the folder to be copied to Photoshop

    try:
        # 1. Clone or update SD-PPP repository
        if os.path.exists(sdppp_repo_path):
            print(f"   Updating SD-PPP repository: {sdppp_repo_path}...")
            subprocess.run(["git", "pull", "--force"], cwd=sdppp_repo_path, check=True)
        else:
            print(f"   Cloning SD-PPP repository: {SD_PPP_REPO} to {sdppp_repo_path}...")
            subprocess.run(["git", "clone", SD_PPP_REPO, sdppp_repo_path], check=True)
        print("✅ SD-PPP repository cloned/updated.")

        # 2. Verify the plugin source path exists
        if not os.path.exists(sdppp_plugin_source_path) or not os.path.isdir(sdppp_plugin_source_path):
            print(f"   ❌ ERROR: SD-PPP Photoshop plugin source directory not found at: {sdppp_plugin_source_path}. Please check the repository structure.")
            return
        if not os.path.exists(os.path.join(sdppp_plugin_source_path, "manifest.json")):
            print(f"   ❌ ERROR: 'manifest.json' not found in SD-PPP Photoshop plugin source directory: {sdppp_plugin_source_path}. This is required for Photoshop plugins.")
            return

        print(f"   Identified plugin source: {sdppp_plugin_source_path}")

        # 3. Copy the plugin folder to all potential Photoshop plugin paths
        photoshop_plugin_paths = [
            "/Library/Application Support/Adobe/CEP/extensions",  # System-level CEP extensions
            os.path.expanduser("~/Library/Application Support/Adobe/CEP/extensions"), # User-level CEP extensions
            "/Applications/Adobe Photoshop 2025/Plug-ins" # Photoshop application-level plugins
        ]

        for dest_path in photoshop_plugin_paths:
            target_plugin_path = os.path.join(dest_path, plugin_folder_name)
            print(f"   Attempting to copy plugin to: {target_plugin_path}...")
            
            try:
                os.makedirs(dest_path, exist_ok=True)
                if os.path.exists(target_plugin_path):
                    print(f"   - Existing plugin found at {target_plugin_path}. Removing before copying.")
                    shutil.rmtree(target_plugin_path)
                shutil.copytree(sdppp_plugin_source_path, target_plugin_path)
                print(f"   ✅ Successfully copied plugin to: {target_plugin_path}")
            except PermissionError:
                print(f"   ⚠️ WARNING: Permission denied to copy to {target_plugin_path}. You may need to run this script with administrator privileges (sudo).")
            except Exception as e:
                print(f"   ❌ ERROR copying plugin to {target_plugin_path}: {e}")

    except subprocess.CalledProcessError as e:
        print(f"   ❌ ERROR during git operation: {e}")
    except Exception as e:
        print(f"   ❌ An unexpected error occurred during SD-PPP plugin installation: {e}")

    print("\n🎉 SD-PPP Plugin Installation Attempt Complete!")
    print("Please remember to restart Photoshop and ComfyUI to ensure all changes take effect.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ComfyUI Photoshop Integration Setup/Uninstall Script.")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall the Photoshop plugin and ComfyUI integration.")
    parser.add_argument("--keep-models", action="store_true", help="When uninstalling, keep downloaded models and LoRAs.")
    parser.add_argument("--uninstall-zxp", action="store_true", help="When uninstalling, also uninstall ZXP Installer via Homebrew.")
    parser.add_argument("--install-sdppp", action="store_true", help="Install the SD-PPP Photoshop plugin.")
    
    args = parser.parse_args()

    if args.uninstall:
        uninstall_photoshop_integration(keep_models=args.keep_models, uninstall_zxp=args.uninstall_zxp)
    elif args.install_sdppp:
        install_sdppp_plugin()
    else:
        # Default installation logic (for comfyui-photoshop)
        install_custom_nodes()
        install_custom_node_dependencies()
        download_models()
        install_photoshop_plugin_manually()
        final_instructions()
