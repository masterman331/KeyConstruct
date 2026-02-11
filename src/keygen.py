import argparse
import secrets
import string
import sys
import pyperclip
import configparser
import os
import math
import json
import csv
import requests
import re
import uuid
import base64
import time
import getpass
from itertools import cycle

try:
    import ulid
    import nanoid
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.backends import default_backend
except ImportError as e:
    print(f"Error: A required library is missing: {e}. Please run the installer or 'pip install -r requirements.txt'.")
    sys.exit(1)

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(SCRIPT_DIR, 'keygen_config.ini')
DICTIONARIES_DIR = os.path.join(SCRIPT_DIR, 'dictionaries')
DESKTOP_PATH = os.path.join(os.path.expanduser('~'), 'Desktop')

# --- Color Themes ---
class Color:
    RESET = '\033[0m'
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = (f'\033[3{i}m' for i in range(8))
    BRIGHT_BLACK, BRIGHT_RED, BRIGHT_GREEN, BRIGHT_YELLOW, BRIGHT_BLUE, BRIGHT_MAGENTA, BRIGHT_CYAN, BRIGHT_WHITE = (f'\033[9{i}m' for i in range(8))

THEMES = {
    'default': {'title': Color.CYAN, 'header': Color.MAGENTA, 'key_output': Color.GREEN, 'error': Color.RED, 'info': Color.YELLOW, 'argument_group': Color.GREEN, 'benchmark': Color.BLUE},
    'hacker': {'title': Color.BRIGHT_GREEN, 'header': Color.GREEN, 'key_output': Color.WHITE, 'error': Color.BRIGHT_RED, 'info': Color.BRIGHT_YELLOW, 'argument_group': Color.BRIGHT_GREEN, 'benchmark': Color.BRIGHT_BLUE},
    'neon': {'title': Color.BRIGHT_MAGENTA, 'header': Color.BRIGHT_CYAN, 'key_output': Color.BRIGHT_YELLOW, 'error': Color.BRIGHT_RED, 'info': Color.BRIGHT_BLUE, 'argument_group': Color.BRIGHT_CYAN, 'benchmark': Color.BRIGHT_YELLOW},
    'minimal': {'title': Color.WHITE, 'header': Color.WHITE, 'key_output': Color.WHITE, 'error': Color.BRIGHT_RED, 'info': Color.BRIGHT_YELLOW, 'argument_group': Color.WHITE, 'benchmark': Color.WHITE}
}

current_theme = 'default'
color_map = THEMES[current_theme]

# --- Global State ---
session_generation_count = 0

# --- Helper Functions ---
def load_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE_PATH):
        config.read(CONFIG_FILE_PATH)
        global current_theme
        current_theme = config.get('settings', 'theme', fallback='default')
        if current_theme not in THEMES:
            current_theme = 'default'
    return config

def save_config(config):
    with open(CONFIG_FILE_PATH, 'w') as configfile:
        config.write(configfile)

def print_colored(text, color_key):
    print(f"{color_map.get(color_key, Color.WHITE)}{text}{Color.RESET}")

def typing_animation(text, delay=0.03):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def calculate_entropy(password, char_set):
    if not password or not char_set: return 0
    charset_size = len(set(char_set))
    if charset_size <= 1: return 0
    entropy = len(password) * math.log2(charset_size)
    return entropy

def apply_case(text, case_style):
    if not case_style: return text
    if case_style == 'upper': return text.upper()
    if case_style == 'lower': return text.lower()
    if case_style == 'alternating':
        return "".join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text))
    if case_style == 'random':
        return "".join(secrets.choice([c.upper, c.lower])() for c in text)
    return text
    
def get_entropy_strength(entropy):
    if entropy >= 128: return "Very Strong"
    if entropy >= 90: return "Strong"
    if entropy >= 60: return "Moderate"
    return "Weak"

# --- Generation Functions ---
def generate_password(length, use_letters, use_numbers, use_special, custom_chars):
    char_set = ''
    if custom_chars:
        char_set = custom_chars
    else:
        if use_letters: char_set += string.ascii_letters
        if use_numbers: char_set += string.digits
        if use_special: char_set += string.punctuation
    if not char_set: raise ValueError("Character set is empty.")
    return ''.join(secrets.choice(char_set) for _ in range(length)), char_set

def load_words(lang_code):
    lang_file = os.path.join(DICTIONARIES_DIR, f"{lang_code.upper()}.txt")
    if not os.path.exists(lang_file):
        raise FileNotFoundError(f"Dictionary for language '{lang_code}' not found. Try --update-dictionaries.")
    
    words = []
    with open(lang_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip().lower()
            if not line or line.startswith('#'):
                continue
            
            # Check for EFF wordlist format (number<tab>word)
            match = re.match(r'^\d+\s+(.*)$', line)
            if match:
                words.append(match.group(1))
            else:
                words.append(line)
    return words

def generate_passphrase(num_words, lang_code, separator='-'):
    words = load_words(lang_code)
    if len(words) < num_words:
        print_colored(f"Warning: Not enough words in '{lang_code}' dictionary. Using all available.", 'info')
        num_words = len(words)
    return separator.join(secrets.SystemRandom().sample(words, num_words))

def generate_from_pattern(pattern_string):
    result, char_set_used = [], ""
    i = 0
    while i < len(pattern_string):
        if pattern_string[i] == '[':
            match = re.match(r'\[word([A-Za-z]{2})\]', pattern_string[i:])
            if match:
                lang_code = match.group(1).lower()
                word = secrets.choice(load_words(lang_code))
                result.append(word)
                i += len(match.group(0))
                continue
        char_type = pattern_string[i]
        char_map = {'A': string.ascii_letters, '9': string.digits, 'S': string.punctuation, 'X': string.ascii_letters + string.digits + string.punctuation}
        if char_type in char_map:
            char_set = char_map[char_type]
            result.append(secrets.choice(char_set))
            char_set_used += char_set
        else:
            result.append(char_type)
        i += 1
    return "".join(result), "".join(set(char_set_used))

# --- Dictionary and File Functions ---
def update_dictionaries():
    # Corrected Czech dictionary URL
    dictionaries = {
        'en': 'https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt',
        'cz': 'https://raw.githubusercontent.com/redhat-developer-demos/quarkus-tutorial-wordlist/main/wordlist-cs.txt',
        'de': 'https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt', # Using large wordlist for DE, ES, FR for now
        'es': 'https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt',
        'fr': 'https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt',
    }
    os.makedirs(DICTIONARIES_DIR, exist_ok=True)
    print_colored("Updating dictionaries...", 'header')
    for lang, url in dictionaries.items():
        try:
            print_colored(f"Downloading {lang.upper()} dictionary...", 'info')
            response = requests.get(url)
            response.raise_for_status()
            with open(os.path.join(DICTIONARIES_DIR, f"{lang.upper()}.txt"), 'wb') as f:
                f.write(response.content)
        except requests.exceptions.RequestException as e:
            print_colored(f"Error downloading {lang.upper()} dictionary: {e}", 'error')
    print_colored("Dictionary update complete.", 'header')

def encrypt_file(filepath, password):
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32, # Fernet requires 32-byte key
        salt=salt,
        iterations=390000,
        backend=default_backend()
    )
    key = Fernet(base64.urlsafe_b64encode(kdf.derive(password.encode())))
    with open(filepath, 'rb') as f:
        data = f.read()
    encrypted_data = key.encrypt(data)
    with open(filepath + ".enc", 'wb') as f:
        f.write(salt + encrypted_data)
    print_colored(f"Encrypted file saved to {filepath}.enc", 'info')

def decrypt_file(filepath_enc, password):
    try:
        with open(filepath_enc, 'rb') as f:
            salt = f.read(16) # Read the 16-byte salt
            encrypted_data = f.read()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32, # Fernet requires 32-byte key
            salt=salt,
            iterations=390000,
            backend=default_backend()
        )
        key = Fernet(base64.urlsafe_b64encode(kdf.derive(password.encode())))
        decrypted_data = key.decrypt(encrypted_data)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}. Check password and file integrity.")


# --- Special Modes ---
def run_benchmark(args):
    print_colored("--- Benchmark Mode ---", 'header')
    num_keys = args.benchmark if args.benchmark > 0 else 1000
    start_time = time.time()
    for _ in range(num_keys):
        generate_password(16, True, True, True, None)
    end_time = time.time()
    duration = end_time - start_time
    kps = num_keys / duration
    print_colored(f"Generated {num_keys} keys in {duration:.4f} seconds.", 'benchmark')
    print_colored(f"Speed: {kps:,.2f} keys per second.", 'benchmark')

def show_stats(config):
    total_gens = config.getint('statistics', 'generation_count', fallback=0)
    print_colored("--- Generation Statistics ---", 'header')
    print_colored(f"Keys generated this session: {session_generation_count}", 'info')
    print_colored(f"Lifetime keys generated: {total_gens + session_generation_count}", 'info')

# --- Main Logic ---
def main():
    global color_map, current_theme, session_generation_count
    config = load_config()
    color_map = THEMES.get(current_theme, THEMES['default'])
    
    parser = argparse.ArgumentParser(description=f"{color_map['title']}KeyConstruct - A professional key generator.{Color.RESET}", formatter_class=argparse.RawTextHelpFormatter)
    
    # Using plain strings for group titles to avoid SyntaxError with f-strings and escape codes
    gen_group = parser.add_argument_group('Key Generation Options')
    gen_group.add_argument('-k', '--keys', type=int, default=1, help='Number of keys.')
    gen_group.add_argument('-l', '--length', type=int, default=12, help='Length of each key.')
    gen_group.add_argument('--custom', type=str, help='Custom character set.')
    gen_group.add_argument('--pattern', type=str, help='Pattern to generate from (e.g., "AA-9999-SS").')
    gen_group.add_argument('--case', choices=['upper', 'lower', 'alternating', 'random'], help='Apply case styling.')

    char_group = parser.add_argument_group('Character Types (for default generation)')
    char_group.add_argument('--letters', action='store_true', help='Include letters.')
    char_group.add_argument('-n', '--numbers', action='store_true', help='Include numbers.')
    char_group.add_argument('-s', '--special', action='store_true', help='Include special characters.')

    preset_group = parser.add_argument_group('Presets')
    preset_group.add_argument('--wifi', action='store_true', help='Strong Wi-Fi password.')
    preset_group.add_argument('--bank', action='store_true', help='Strong banking password.')
    preset_group.add_argument('--uuid', action='store_true', help='Generate a UUID.')
    preset_group.add_argument('--ulid', action='store_true', help='Generate a ULID.')
    preset_group.add_argument('--nano-id', action='store_true', help='Generate a Nano ID.')
    preset_group.add_argument('--hex', type=int, metavar='LEN', help='Hexadecimal key of length LEN.')
    preset_group.add_argument('--pin', type=int, metavar='LEN', help='Numeric PIN of length LEN.')
    preset_group.add_argument('--memorable', action='store_true', help='Memorable password like "word-word-99!".')

    passphrase_group = parser.add_argument_group('Passphrase Options')
    passphrase_group.add_argument('--words', type=int, metavar='N', help='Passphrase with N words.')
    passphrase_group.add_argument('--lang', type=str, default='en', help='Language for passphrase (default: en).')
    passphrase_group.add_argument('--update-dictionaries', action='store_true', help='Download/update dictionary files.')

    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument('--json', action='store_true', help='JSON output.')
    output_group.add_argument('--csv', action='store_true', help='CSV output.')
    output_group.add_argument('--plain', action='store_true', help='Plain text output.')
    output_group.add_argument('--output', type=str, metavar='FILE', help='Save output to FILE.')
    output_group.add_argument('--copy', action='store_true', help='Copy output to clipboard.')
    output_group.add_argument('--encrypt', type=str, metavar='PASS', nargs='?', const=True, help='Encrypt output file with a password.')
    output_group.add_argument('--decrypt', type=str, metavar='FILE', help='Decrypt an encrypted file.')
    output_group.add_argument('--show-decrypted', action='store_true', help='Show decrypted content in terminal.')
    output_group.add_argument('--output-decrypted', type=str, metavar='FILE', help='Save decrypted content to a new file.')

    misc_group = parser.add_argument_group('Miscellaneous')
    misc_group.add_argument('--theme', choices=THEMES.keys(), help='Set color theme and save preference.')
    misc_group.add_argument('--stats', action='store_true', help='Show generation statistics.')
    misc_group.add_argument('--benchmark', type=int, metavar='N', nargs='?', const=1000, help='Run a generation benchmark for N keys.')
    misc_group.add_argument('--animate', action='store_true', help='Enable typing animation for output.')
    parser.add_argument('--version', action='version', version='%(prog)s 2.0')
    
    args = parser.parse_args()

    # Handle decryption mode first
    if args.decrypt:
        if not os.path.exists(args.decrypt):
            print_colored(f"Error: Decryption file '{args.decrypt}' not found.", 'error')
            sys.exit(1)
        password = getpass.getpass("Enter decryption password: ")
        try:
            decrypted_content = decrypt_file(args.decrypt, password)
            if args.show_decrypted:
                print_colored("--- Decrypted Content ---", 'header')
                print(decrypted_content)
                print_colored("-------------------------", 'header')
            if args.output_decrypted:
                with open(args.output_decrypted, 'w', encoding='utf-8') as f:
                    f.write(decrypted_content)
                print_colored(f"Decrypted content saved to {args.output_decrypted}", 'info')
            if not args.show_decrypted and not args.output_decrypted:
                print_colored("Decrypted content not displayed or saved. Use --show-decrypted or --output-decrypted.", 'info')
        except ValueError as e:
            print_colored(f"Decryption Error: {e}", 'error')
        sys.exit(0)

    if args.theme:
        current_theme = args.theme
        color_map = THEMES[current_theme]
        if 'settings' not in config: config.add_section('settings')
        config.set('settings', 'theme', current_theme)
        save_config(config)
        print_colored(f"Theme set to '{current_theme}'.", 'info')

    if args.update_dictionaries:
        update_dictionaries()
        sys.exit(0)
        
    if args.benchmark is not None:
        run_benchmark(args)
        sys.exit(0)

    if args.stats:
        show_stats(config)
        sys.exit(0)

    # --- Generation Logic ---
    try:
        if args.wifi:
            args.pattern = 'AANS-AANS-AANS-AANS' # WPA2-Personal typically 8-63 chars, complex. Sets pattern.
            args.length = 16 # Explicitly set length for presets
        if args.bank:
            args.pattern = 'ANANANANAN' # Example bank pattern: letters, numbers. Simplified.
            args.length = 10 # Explicitly set length for presets
        if args.memorable: args.pattern = '[wordEN]-[wordEN]-99S'
        
        mode = 'default'
        if args.words: mode = 'words'
        elif args.pattern: mode = 'pattern'
        elif args.uuid: mode = 'uuid'
        elif args.ulid: mode = 'ulid'
        elif args.nano_id: mode = 'nano_id'
        elif args.hex is not None: mode = 'hex'
        elif args.pin is not None: mode = 'pin'

        generated_items = []
        should_animate = args.animate and not any([args.json, args.csv, args.plain, args.output])
        
        if should_animate and args.keys > 5:
            print_colored("Warning: Animation with many keys might take a long time.", 'info')
            time.sleep(1) # Give user time to read warning
        
        for _ in range(args.keys):
            key, entropy, strength = "", 0, "N/A"
            char_set_for_entropy = ""

            if mode == 'words':
                key = generate_passphrase(args.words, args.lang)
                # Word-based passphrases have their own entropy calculation,
                # but for simplicity of uniform output structure, we'll assign
                # a high value if words are from a sufficiently large dictionary.
                # Assuming EFF wordlist is ~7776 words.
                entropy = args.words * math.log2(7776) if args.words > 0 else 0
            elif mode == 'pattern':
                key, char_set_for_entropy = generate_from_pattern(args.pattern)
            elif mode == 'uuid':
                key = str(uuid.uuid4())
                entropy = 122 # UUIDv4 has 122 random bits
            elif mode == 'ulid':
                key = str(ulid.new())
                entropy = 128 # ULID has 128 bits of entropy (time + randomness)
            elif mode == 'nano_id':
                key = nanoid.generate(size=args.length if args.length != 12 else 21) # NanoID default size 21
                # NanoID uses a 64-character alphabet by default.
                # Entropy = length * log2(alphabet_size)
                entropy = len(key) * math.log2(64)
            elif mode == 'hex':
                if args.hex <= 0: raise ValueError("Hex key length must be a positive integer.")
                key = secrets.token_hex(math.ceil(args.hex / 2))[:args.hex]
                char_set_for_entropy = string.hexdigits
            elif mode == 'pin':
                if args.pin <= 0: raise ValueError("PIN length must be a positive integer.")
                key = ''.join(secrets.choice(string.digits) for _ in range(args.pin))
                char_set_for_entropy = string.digits
            else: # mode == 'default' (includes wifi/bank presets which set args.pattern)
                # Only apply default char types if no other explicit generation options are set.
                if not (args.letters or args.numbers or args.special or args.custom or args.pattern): # FIX: added args.pattern here
                    args.letters = args.numbers = args.special = True
                key, char_set_for_entropy = generate_password(args.length, args.letters, args.numbers, args.special, args.custom)

            key = apply_case(key, args.case)
            
            # Recalculate entropy for default/pattern if not set by specific modes
            if mode not in ['words', 'uuid', 'ulid', 'nano_id'] and char_set_for_entropy:
                entropy = calculate_entropy(key, char_set_for_entropy)
            
            strength = get_entropy_strength(entropy)
            generated_items.append({"key": key, "entropy_bits": round(entropy, 2), "strength": strength})
            session_generation_count += 1

        if should_animate: typing_animation("--- Generated Items ---", 0.01)
        for i, item in enumerate(generated_items):
            output_str = f"  {i+1:02d}: {item['key']}"
            if item['entropy_bits'] > 0: output_str += f" (Entropy: {item['entropy_bits']} bits - {item['strength']})"
            if should_animate: typing_animation(output_str)
            elif not any([args.json, args.csv, args.plain, args.output]): print_colored(output_str, 'key_output')
        if should_animate: typing_animation("-----------------------", 0.01)

        # --- Output Handling ---
        output_content = ""
        if args.json:
            output_content = json.dumps(generated_items, indent=2)
        elif args.csv:
            from io import StringIO
            s_io = StringIO()
            if mode == 'words': # Specific handling for passphrases
                writer = csv.writer(s_io)
                writer.writerow(["passphrase", "entropy_bits", "strength"]) # Correct header for passphrases
                for item in generated_items:
                    writer.writerow([item['key'], item['entropy_bits'], item['strength']]) # Extract only the 'key' value
            elif generated_items and isinstance(generated_items[0], dict): # All other cases with structured output
                fieldnames = list(generated_items[0].keys())
                writer = csv.DictWriter(s_io, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(generated_items)
            else: # Fallback for any other non-dict items (shouldn't happen with current design)
                writer = csv.writer(s_io)
                writer.writerow(["item"])
                for item in generated_items:
                    writer.writerow([item])
            output_content = s_io.getvalue()
        elif args.plain or (args.output and not any([args.json, args.csv])): # plain output or default for file output
            output_content = "\n".join([item["key"] for item in generated_items])

        if output_content and not should_animate and not args.output and not any([args.json, args.csv, args.plain]):
            # This block is for default print if no output format and no animation
            for item in generated_items:
                output_str = f"{item['key']}" # default no prefix
                print_colored(output_str, 'key_output')
        elif output_content and not args.output: # Print to console for explicit json/csv/plain if not writing to file
             print(output_content)


        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f: f.write(output_content)
            print_colored(f"Output saved to {args.output}", 'info')
            if args.encrypt:
                password = args.encrypt if isinstance(args.encrypt, str) else getpass.getpass("Enter encryption password: ")
                encrypt_file(args.output, password)
                os.remove(args.output) # Remove unencrypted file

        if args.copy:
            pyperclip.copy("\n".join([item["key"] for item in generated_items]))
            print_colored("Generated item(s) copied to clipboard.", 'info')

    except Exception as e:
        print_colored(f"Error: {e}", 'error')
        sys.exit(1)
    finally:
        if 'statistics' not in config: config.add_section('statistics')
        total_gens = config.getint('statistics', 'generation_count', fallback=0)
        config.set('statistics', 'generation_count', str(total_gens + session_generation_count))
        save_config(config)

if __name__ == "__main__":
    if os.name == 'nt': os.system('')
    main()