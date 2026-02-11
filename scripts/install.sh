
#!/bin/bash

# --- Configuration ---
APP_NAME="KeyConstruct"
SCRIPT_NAME="keygen.py"
INSTALL_NAME="keygen"
# Use a standard directory for user-local binaries.
INSTALL_DIR="$HOME/.local/bin"
SOURCE_SCRIPT_PATH="$(dirname "$0")/../src/$SCRIPT_NAME"

# --- Colors for output ---
COLOR_RESET='\033[0m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[0;33m'
COLOR_RED='\033[0;31m'
COLOR_CYAN='\033[0;36m'

echo_green() {
    echo -e "${COLOR_GREEN}$1${COLOR_RESET}"
}
echo_yellow() {
    echo -e "${COLOR_YELLOW}$1${COLOR_RESET}"
}
echo_red() {
    echo -e "${COLOR_RED}$1${COLOR_RESET}"
}
echo_cyan() {
    echo -e "${COLOR_CYAN}$1${COLOR_RESET}"
}


# --- Installation ---
echo_cyan "
 Installing $APP_NAME..."
echo_cyan " ================================
"

# 1. Create installation directory
if [ ! -d "$INSTALL_DIR" ]; then
    echo_green "[+] Creating installation directory: $INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
    if [ $? -ne 0 ]; then
        echo_red "[!] ERROR: Failed to create directory. Aborting."
        exit 1
    fi
else
    echo_yellow "[*] Installation directory already exists."
fi

# 2. Copy the script and requirements.txt and make it executable
echo_green "[+] Copying script to $INSTALL_DIR/$INSTALL_NAME"
cp "$SOURCE_SCRIPT_PATH" "$INSTALL_DIR/$INSTALL_NAME"
if [ $? -ne 0 ]; then
    echo_red "[!] ERROR: Failed to copy script. Make sure it exists at $SOURCE_SCRIPT_PATH."
    exit 1
fi

echo_green "[+] Copying requirements.txt to $INSTALL_DIR/requirements.txt"
cp "$(dirname "$0")/../requirements.txt" "$INSTALL_DIR/requirements.txt"
if [ $? -ne 0 ]; then
    echo_red "[!] ERROR: Failed to copy requirements.txt. Make sure it exists."
    exit 1
fi

echo_green "[+] Installing Python dependencies from requirements.txt..."
python3 -m pip install -r "$INSTALL_DIR/requirements.txt"
if [ $? -ne 0 ]; then
    echo_red "[!] ERROR: Failed to install Python dependencies. Please ensure pip is installed and accessible."
    exit 1
fi

echo_green "[+] Making the script executable..."
chmod +x "$INSTALL_DIR/$INSTALL_NAME"
if [ $? -ne 0 ]; then
    echo_red "[!] ERROR: Failed to make script executable."
    exit 1
fi

# 3. Check and update PATH
SHELL_CONFIG=""
if [ -n "$BASH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
elif [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
else
    SHELL_CONFIG="$HOME/.profile"
fi

echo_green "[+] Checking user PATH in $SHELL_CONFIG..."
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo_yellow "[!] '$INSTALL_DIR' not found in your PATH."
    echo_green "[+] Adding it to $SHELL_CONFIG"
    
    # Append the export command to the shell config file
    echo -e "
# Add KeyConstruct to PATH" >> "$SHELL_CONFIG"
    echo "export PATH="\$PATH:$INSTALL_DIR"" >> "$SHELL_CONFIG"
    
    PATH_MSG="Please restart your terminal or run 'source $SHELL_CONFIG' for the changes to take effect."
else
    echo_yellow "[*] '$INSTALL_DIR' is already in your PATH."
    PATH_MSG=""
fi

echo_cyan "
 ================================"
echo_green " $APP_NAME installation complete!"
echo_cyan " ================================
"

echo " You can now use the '$INSTALL_NAME' command from anywhere."
if [ -n "$PATH_MSG" ]; then
    echo_yellow "
 IMPORTANT: $PATH_MSG"
fi
echo ""

exit 0

