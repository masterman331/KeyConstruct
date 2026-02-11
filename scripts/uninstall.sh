
#!/bin/bash

# --- Configuration ---
APP_NAME="KeyConstruct"
INSTALL_NAME="keygen"
INSTALL_DIR="$HOME/.local/bin"

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

# --- Uninstallation ---
echo_cyan "
 Uninstalling $APP_NAME..."
echo_cyan " ================================
"

# 1. Remove the executable script
if [ -f "$INSTALL_DIR/$INSTALL_NAME" ]; then
    echo_green "[+] Deleting executable: $INSTALL_DIR/$INSTALL_NAME"
    rm "$INSTALL_DIR/$INSTALL_NAME"
    if [ $? -ne 0 ]; then
        echo_red "[!] WARNING: Failed to delete $INSTALL_DIR/$INSTALL_NAME. You may need to delete it manually."
    else
        echo_green "[*] Executable deleted successfully."
    fi
else
    echo_yellow "[*] Executable not found at $INSTALL_DIR/$INSTALL_NAME. Nothing to delete."
fi

# 2. Remove the installation directory from PATH in shell config files
echo_green "[+] Removing PATH entry from shell configuration files..."
SHELL_CONFIGS=("$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile")
PATH_UPDATED=false

for config_file in "${SHELL_CONFIGS[@]}"; do
    if [ -f "$config_file" ]; then
        if grep -q "export PATH=.*$INSTALL_DIR" "$config_file" || grep -q "# Add KeyConstruct to PATH" "$config_file"; then
            echo_green "  [*] Modifying $config_file..."
            # Use sed to remove the lines related to KeyConstruct PATH export
            # -i option for in-place editing
            sed -i.bak '/# Add KeyConstruct to PATH/{N;d;}' "$config_file" # Removes comment and the next line (export PATH)
            sed -i.bak "\_export PATH=.*$INSTALL_DIR_d" "$config_file" # Removes just the export line if comment is not found or already removed
            
            # Clean up potential duplicate lines if any
            sed -i.bak '/^export PATH=".*:.*"$/!b; :a; s/\(.*:\)\(.*\1\)\(:\)/\1\2\3/; ta' "$config_file"
            
            # Remove backup file if sed created one
            rm -f "${config_file}.bak"
            PATH_UPDATED=true
            echo_green "  [*] PATH entry removed from $config_file."
        else
            echo_yellow "  [*] No KeyConstruct PATH entry found in $config_file."
        fi
    fi
done

if [ "$PATH_UPDATED" = true ]; then
    echo_green "[*] PATH entries removed successfully."
    echo_yellow "[!] This change will take effect in new terminal sessions."
else
    echo_yellow "[*] No PATH changes were required."
fi

echo_cyan "
 ================================"
echo_green " $APP_NAME uninstallation complete!"
echo_cyan " ================================
"
echo " Please restart your terminal sessions to ensure all changes take effect."
echo ""

exit 0
