# KeyConstruct

A powerful, professional, and customizable command-line tool for generating secure random keys, passwords, and human-readable passphrases.

## Features

-   **Secure**: Uses Python's `secrets` module for generating cryptographically strong random data, ensuring high-quality randomness.
-   **Customizable**: Control the length, character types (letters, numbers, special characters), and number of keys.
-   **Presets**: Quickly generate keys for common use cases like Wi-Fi, banking, UUIDs, ULIDs, Nano IDs, Hexadecimal keys, or PINs with predefined secure settings.
-   **Pattern-based Generation**: Define custom key structures using a flexible pattern language (e.g., "AA-9999-SS", "[wordEN]-LLLNNN").
-   **Case Patterns**: Apply various case styles (uppercase, lowercase, alternating, random) to generated keys.
-   **Animated Output (Opt-in)**: Enjoy a sleek "typing" animation for interactive key generation when explicitly enabled.
-   **Secure File Output**: Encrypt generated keys into files using a password, with documentation on how to decrypt.
-   **Output Formats**: Save generated keys in various formats (plain text, JSON, CSV) to files or display directly.
-   **Clipboard Integration**: Instantly copy generated keys to your system clipboard for convenience.
-   **Color Themes**: Personalize your CLI experience with different color themes (hacker, neon, minimal) and save your preference.
-   **Entropy Meter**: Get an immediate security assessment of your generated keys with an entropy calculation, providing insights into their strength.
-   **Human-Readable Passphrases**: Generate memorable passphrases using word lists from multiple languages, enhancing both security and usability.
-   **Generation Statistics**: Track how many keys you've generated in a session and over the lifetime of the tool.
-   **Benchmark Mode**: Test the speed and performance of key generation.
-   **Portable**: Cross-platform installation scripts to add the tool to your system's PATH.

## Installation

KeyConstruct requires Python 3.7+ and a few external Python libraries.

### Windows

1.  Open a Command Prompt or PowerShell.
2.  Navigate to the `scripts` directory within the project folder.
3.  Run the installer:
    ```cmd
    .\install.bat
    ```
4.  Restart your terminal for the PATH changes to take effect. The `keygen` command will now be available globally.

### Linux / macOS

1.  Open a terminal.
2.  Navigate to the `scripts` directory within the project folder.
3.  Make the installer executable:
    ```sh
    chmod +x install.sh
    ```
4.  Run the installer:
    ```sh
    ./install.sh
    ```
5.  Restart your terminal or source your shell's configuration file (e.g., `source ~/.bashrc`) for the changes to take effect. The `keygen` command will now be available globally.

## Usage

Once installed, you can use the `keygen` command from anywhere in your terminal.

### Basic Syntax

```
keygen [options]
```

### Arguments

| Argument | Short Form | Description | Default |
| :------- | :--------- | :---------- | :------ |
| `--keys` | `-k` | Number of keys/passphrases to generate. | `1` |
| `--length` | `-l` | Length of each key. (Ignored for passphrases, UUIDs, ULIDs, Nano IDs, patterns) | `12` |
| `--letters` | | Include letters (a-z, A-Z). | `True`\* |
| `--numbers` | `-n` | Include numbers (0-9). | `True`\* |
| `--special` | `-s` | Include special characters (!@#$...). | `True`\* |
| `--custom` | | A custom set of characters to generate keys from. | `None` |
| `--pattern` | | Generate key based on a pattern (e.g., "AA-9999-SS", "[wordEN]-LLLNNN"). | `None` |
| `--case` | | Apply case styling (`upper`, `lower`, `alternating`, `random`). | `None` |
| `--wifi` | | Generate a strong Wi-Fi password (preset: 16 chars, letters, numbers, special). | `False` |
| `--bank` | | Generate a strong banking password (preset: 16 chars, letters, numbers). | `False` |
| `--uuid` | | Generate a UUID (Universally Unique Identifier). | `False` |
| `--ulid` | | Generate a ULID (Universally Unique Lexicographically Sortable Identifier). | `False` |
| `--nano-id` | | Generate a Nano ID (a tiny, secure, URL-friendly unique string ID). | `False` |
| `--hex` | | Generate a hexadecimal key of specified length. | `None` |
| `--pin` | | Generate a numeric PIN of specified length. | `None` |
| `--memorable` | | Generate a memorable password (preset: "word-word-99!"). | `False` |
| `--words` | | Generate a human-readable passphrase with N words. | `None` |
| `--lang` | | Language for passphrase dictionary (e.g., `en`, `cz`). | `en` |
| `--update-dictionaries` | | Download or update dictionary files for passphrases. | `False` |
| `--json` | | Output keys/passphrases in JSON format. | `False` |
| `--csv` | | Output keys/passphrases in CSV format. | `False` |
| `--plain` | | Output keys/passphrases in plain text format (default if no other format specified). | `False` |
| `--output` | | Specify an output file to save the generated content. | `None` |
| `--copy` | | Copy the last generated key/passphrase (or all, if multiple) to clipboard. | `False` |
| `--encrypt` | | Encrypt the output file with a password. Can specify password or be prompted. | `None` |
| `--theme` | | Set color theme (`default`, `hacker`, `neon`, `minimal`). Saves preference. | `default` |
| `--stats` | | Show generation statistics for the current session and lifetime. | `False` |
| `--benchmark` | | Run a generation benchmark for N keys (default 1000). | `False` |
| `--animate` | | Enable typing animation for output. | `False` |
| `--version` | | Show program's version number and exit. | |
| `--help` | `-h` | Show the help message and exit. | |

\* **Note**: If no character types (`--letters`, `--numbers`, `--special`, `--custom`) are specified, and `--words`, `--pattern`, or any presets are not used, all types (letters, numbers, special) are included by default.

### Pattern Generation Syntax

The `--pattern` argument allows for highly flexible key generation:

-   `A`: Represents an uppercase or lowercase letter (`a-z`, `A-Z`).
-   `9`: Represents a digit (`0-9`).
-   `S`: Represents a special character (from `string.punctuation`).
-   `X`: Represents any character (letter, number, or special character).
-   `[wordXX]`: Represents a word from the specified language dictionary (e.g., `[wordEN]` for English, `[wordCZ]` for Czech).
-   Any other character: Will be included literally in the generated key.

### Secure File Output (`--encrypt`)

When using `--output <file>` along with `--encrypt`, `KeyConstruct` will encrypt the generated content before saving it to the specified file. If `--encrypt` is provided without a password, you will be prompted to enter one securely.

**Decryption using OpenSSL (Linux/macOS/WSL):**

`KeyConstruct` uses Fernet symmetric encryption. You can decrypt the file using Python, but for quick command-line decryption (e.g., on Linux/macOS/WSL), you can use `openssl` if you derive the key correctly. However, due to the complexity of key derivation (PBKDF2HMAC with salt), directly decrypting with a standard `openssl enc` command can be challenging.

**Recommended Decryption Method (Python):**

For reliable decryption, it's recommended to use a small Python script. You would need the password and the original salt (which is stored at the beginning of the encrypted file).

Example Python decryption snippet:
```python
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

def decrypt_file(filepath_enc, password):
    with open(filepath_enc, 'rb') as f:
        salt = f.read(16) # Read the 16-byte salt
        encrypted_data = f.read()

    kdf = PBKDF2HMAC(hashes.SHA256(), 390000, salt, default_backend())
    key = Fernet(base64.urlsafe_b64encode(kdf.derive(password.encode())))
    decrypted_data = key.decrypt(encrypted_data)
    return decrypted_data.decode('utf-8') # Assuming UTF-8 content

# Usage
# file_to_decrypt = "output.txt.enc"
# encryption_password = "your_strong_password"
# decrypted_content = decrypt_file(file_to_decrypt, encryption_password)
# print(decrypted_content)
```

### Examples

**1. Generate a single default key (12 chars, all character types) with entropy:**
```
keygen
```

**2. Generate 5 keys, each 16 characters long, with numbers and special characters:**
```
keygen -k 5 -l 16 -n -s
```

**3. Generate a 20-character key with only letters and numbers, in uppercase:**
```
keygen -l 20 --letters -n --case upper
```

**4. Generate a key using a custom character set:**
```
keygen -l 8 --custom "abcdef123456"
```

**5. Generate a strong Wi-Fi password:**
```
keygen --wifi
```

**6. Generate a strong banking password:**
```
keygen --bank
```

**7. Generate a memorable password like "word-word-99!":**
```
keygen --memorable
```

**8. Generate a UUID:**
```
keygen --uuid
```

**9. Generate a ULID:**
```
keygen --ulid
```

**10. Generate a Nano ID:**
```
keygen --nano-id
```

**11. Generate a 32-character hexadecimal key:**
```
keygen --hex 32
```

**12. Generate a 6-digit PIN:**
```
keygen --pin 6
```

**13. Generate a key matching the pattern "AA-9999-SS":**
```
keygen --pattern "AA-9999-SS"
```

**14. Generate a key combining an English word, letters, and numbers:**
```
keygen --pattern "[wordEN]-LLLNNN"
```

**15. Generate a 32-character key and instantly copy it to the clipboard:**
```
keygen -l 32 --copy
```

**16. Generate a 4-word human-readable passphrase (English default):**
```
keygen --words 4
```

**17. Generate a 5-word human-readable passphrase in Czech:**
```
keygen --words 5 --lang cz
```

**18. Download or update dictionary files (run once before using `--words` for new languages):**
```
keygen --update-dictionaries
```

**19. Output 2 generated keys to a JSON file:**
```
keygen -k 2 --output keys.json --json
```

**20. Output 3 generated keys to a CSV file:**
```
keygen -k 3 --output passwords.csv --csv
```

**21. Generate 1000 keys and export to CSV for load testing/automation:**
```
keygen -k 1000 --csv output.csv
```

**22. Generate keys and save them to an encrypted file, prompting for a password:**
```
keygen -k 10 --output secret_keys.txt --encrypt
```

**23. Set the 'hacker' color theme (this preference will be saved):**
```
keygen --theme hacker
```

**24. Show generation statistics:**
```
keygen --stats
```

**25. Run a generation benchmark (generates 5000 keys):**
```
keygen --benchmark 5000
```

**26. Enable typing animation for output:**
```
keygen --animate -k 3
```

### Configuration

`KeyConstruct` saves your preferred color theme and lifetime generation statistics in a file named `keygen_config.ini` located in the same directory as the `keygen.py` script. This ensures your preferences and stats persist across sessions.

### Dictionary Management

The tool manages word dictionaries in a `dictionaries/` subdirectory next to the `keygen.py` script.
You can add your own dictionary files to this directory. Ensure they are named with a two-letter language code (e.g., `ZH.txt` for Chinese) and contain one word per line. These custom dictionaries will automatically become available for use with the `--lang` option.

## Uninstallation

### Windows

1.  Open a Command Prompt or PowerShell.
2.  Navigate to the `scripts` directory within the project folder:
    ```cmd
    cd ~\scripts\
    ```
3.  Run the uninstaller:
    ```cmd
    .\uninstall.bat
    ```
4.  Restart your terminal for the PATH changes to take effect. The `keygen` command will no longer be available.

### Linux / macOS

1.  Open a terminal.
2.  Navigate to the `scripts` directory within the project folder:
    ```sh
    cd ~\scripts/
    ```
3.  Make the uninstaller executable:
    ```sh
    chmod +x uninstall.sh
    ```
4.  Run the uninstaller:
    ```sh
    ./uninstall.sh
    ```
5.  Restart your terminal or source your shell's configuration file (e.g., `source ~/.bashrc`) for the changes to take effect. The `keygen` command will no longer be available.

---
**Note on Linux/macOS Testing:** This tool has primarily been developed and tested on Windows environments. While the `install.sh` and `uninstall.sh` scripts are designed to be compatible with Linux/macOS, thorough testing on these platforms has not been performed. If you encounter any issues, please report them.

> **Disclaimer:**  
> This project has been vibe-coded please use it cautiously. - masterman331
