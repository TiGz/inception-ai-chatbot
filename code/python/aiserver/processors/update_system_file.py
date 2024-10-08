import os
from utils.partial_file_utils import PartialFileUtils
from bots.file_fixing_bot import FileFixingBot

def update_system_file(system_root_dir: str, file_path: str, file_content: str, target_dir: str = None) -> None:
    """
    Update a system file, checking for partial content and invoking the file fixing bot if necessary.
    Ignores files where the path contains '__snippets/'.

    Args:
        system_root_dir (str): The root directory of the system
        file_path (str): The path of the file to update, relative to the system root
        file_content (str): The new content for the file
        target_dir (str, optional): The target directory to save the file, if different from system_root_dir

    Raises:
        FileNotFoundError: If the file doesn't exist and partial content is detected
        Exception: For any other errors during the update process
    """
    print(f"[DEBUG] Updating system file: {file_path}")
    print(f"[DEBUG] System root directory: {system_root_dir}")
    print(f"[DEBUG] Target directory: {target_dir}")

    # Check if the file path contains '__snippets/'
    if '__snippets/' in file_path:
        print(f"[INFO] Ignoring file in __snippets/: {file_path}")
        return

    if target_dir:
        full_path = os.path.join(target_dir, file_path)
    else:
        full_path = os.path.join(system_root_dir, file_path)
    print(f"[DEBUG] Full file path: {full_path}")

    # Check if the file content is partial using PartialFileUtils
    is_partial = PartialFileUtils.is_partial_file_content(file_content)
    print(f"[DEBUG] Is file content partial? {is_partial}")

    if is_partial:
        print("[DEBUG] Handling partial file content")
        # Check if the file already exists
        if not os.path.exists(full_path):
            print(f"[ERROR] Cannot update non-existent file with partial content: {file_path}")
            raise FileNotFoundError(f"Cannot update non-existent file with partial content: {file_path}")

        # Invoke the file fixing bot
        file_fixing_bot = FileFixingBot()
        if file_fixing_bot is None:
            print("[ERROR] File fixing bot not found")
            raise Exception("File fixing bot not found")

        print("[DEBUG] Reading original file content")
        # Read the original content
        with open(full_path, 'r', encoding='utf-8') as f:
            original_content = f.read()

        print("[DEBUG] Preparing input for file fixing bot")
        # Prepare the input for the file fixing bot
        bot_input = f"""<-- Original File Start -->
{original_content}
<-- End of original file and start of diff to apply -->
{file_content}
<-- End of diff that needs applying to the original file -->"""

        print("[DEBUG] Processing content using file fixing bot")
        # Process the content using the file fixing bot
        processed_content = file_fixing_bot.process_request_sync_final_only(bot_input, "")
        if PartialFileUtils.is_partial_file_content(processed_content):
            print("[ERROR] File fixing bot returned partial content")
            raise Exception("File fixing bot failed to fix the partial file content")

        print("[DEBUG] File fixing bot processing complete")
    else:
        print("[DEBUG] Using provided content as is (not partial)")
        # If not partial, use the provided content as is
        processed_content = file_content

    print(f"[DEBUG] Writing processed content to file: {full_path}")
    # Write the processed content to the file
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(processed_content)

    print(f"[DEBUG] Successfully updated file: {file_path}")