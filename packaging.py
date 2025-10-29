import PyInstaller.__main__
import os
import platform
import shutil

# --- Configuration ---
APP_NAME = "ChronoAI"
SCRIPT_NAME = "main.py"
SRC_DIR = "src"
ICON_NAME = "icon.png"
ASSETS_DIR = "assets"

def main():
    """Runs the PyInstaller packaging process."""
    # --- Paths ---
    script_path = os.path.join(SRC_DIR, SCRIPT_NAME)
    icon_path = os.path.join(ASSETS_DIR, ICON_NAME)

    # --- PyInstaller Command Arguments ---
    command = [
        '--name', APP_NAME,
        '--onefile',
        '--windowed',  # Use '--noconsole' on Windows, this is an alias
        f'--icon={icon_path}',
    ]

    # --- Add Data (Assets) ---
    # The separator for --add-data is platform-dependent (';' on Windows, ':' on others)
    data_separator = ';' if platform.system() == 'Windows' else ':'
    command.extend([
        '--add-data', f'{ASSETS_DIR}{data_separator}{ASSETS_DIR}'
    ])

    # --- Add Hidden Imports ---
    # PyInstaller sometimes misses these, especially for libraries with plugins.
    hidden_imports = [
        'pkg_resources.py2_warn',
        'keyring.backends.Windows.WinVaultKeyring',  # For Windows
        'keyring.backends.macOS.Keyring',            # For macOS
        'keyring.backends.SecretService.Keyring',    # For Linux
        'pyttsx3.drivers.sapi5',                     # For Windows TTS
        'pyttsx3.drivers.nsss',                      # For macOS TTS
        'pyttsx3.drivers.espeak',                    # For Linux TTS
    ]

    for hidden_import in hidden_imports:
        command.extend(['--hidden-import', hidden_import])

    # --- Add the main script ---
    command.append(script_path)

    # --- Run PyInstaller ---
    print(f"Running PyInstaller with command:\n{' '.join(command)}\n")
    PyInstaller.__main__.run(command)

    print("\nPackaging complete. Check the 'dist' folder for the executable.")
    print("Cleaning up build files...")
    shutil.rmtree('build', ignore_errors=True)
    os.remove(f'{APP_NAME}.spec')
    print("Cleanup complete.")

if __name__ == '__main__':
    main()