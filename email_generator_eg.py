import random
import requests
import logging
import datetime
import re
from tqdm import tqdm

# Set up logging
def configure_logging():
    """
    Configures logging settings to log information to a file named 'email_generator.log'.
    """
    logging.basicConfig(filename='email_generator.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
INCLUDE_DOT_PROBABILITY = 0.3
MIN_RANDOM_NUMBER = 100
MAX_RANDOM_NUMBER = 999
MAX_RETRIES = 3
SUPPORT_EMAIL = "Demonofinternet0@gmail.com"
YOUTUBE_CHANNEL = "DemonofInternet"
FILE_NAME = "Email Generator EG"
VERSION = "1.0"
WELCOME_MSG = "Welcome to the Email Generator EG! This tool creates random email addresses for you."

CREDIT_SECTION = """
********** Created By Telegram ID: @Doimous **********
Donate to Bitcoin: 1PhgZqoWxr33mTSGefB1dW3QhjLVrG4MCV
Donate to USDT TRON(TRC20): TCXRkkQ27xdHUxTnEM1WJdneJfHtU4vpPo

For assistance and support, please reach out to Demonofinternet0@gmail.com
"""

VALID_USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9._-]+$')

def get_random_name():
    """
    Fetches a random first and last name from an external API.

    Returns:
    tuple: A tuple containing the first and last name.
    """
    api_url = "https://randomuser.me/api/"

    for _ in range(MAX_RETRIES):
        try:
            response = requests.get(api_url)
            response.raise_for_status()

            data = response.json()
            results = data.get('results', [])

            if not results:
                raise ValueError("Invalid response format: No results found")

            first_name = results[0].get('name', {}).get('first')
            last_name = results[0].get('name', {}).get('last')

            if not first_name or not last_name:
                raise ValueError("Invalid response format: Missing first or last name")

            return first_name, last_name

        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as req_err:
            logging.error(f"An error occurred: {req_err}")
        except ValueError as val_err:
            logging.error(f"ValueError in get_random_name: {val_err}")

    logging.error(f"Failed to retrieve a random name after {MAX_RETRIES} attempts.")
    return None, None

def is_valid_username(username):
    """
    Checks if a given username follows a valid pattern.

    Args:
    username (str): The username to be validated.

    Returns:
    bool: True if the username is valid, False otherwise.
    """
    return bool(VALID_USERNAME_REGEX.match(username))

def generate_email(provider, num_emails, include_dot=True):
    """
    Generates a list of email addresses based on the specified provider and parameters.

    Args:
    provider (str): The email provider (e.g., 'gmail', 'hotmail').
    num_emails (int): The number of email addresses to generate.
    include_dot (bool): If True, includes a dot in the email address.

    Returns:
    tuple: A tuple containing the list of generated email addresses and the count of skipped emails.
    """
    emails = []
    skipped_count = 0

    # Use tqdm for a progress bar
    progress_bar = tqdm(total=num_emails, desc=f'Generating {provider.capitalize()} emails', position=0, leave=True)

    for _ in range(num_emails):
        first_name, last_name = get_random_name()

        random_number = random.randint(MIN_RANDOM_NUMBER, MAX_RANDOM_NUMBER)

        username = f"{first_name.lower()}.{last_name.lower()}.{random_number}" if include_dot and random.random() < INCLUDE_DOT_PROBABILITY else f"{first_name.lower()}{last_name.lower()}{random_number}"

        if not is_valid_username(username):
            logging.warning(f"Invalid characters found in the generated username: {username}. Skipping this email.")
            skipped_count += 1
            continue

        email_domain = {
            'gmail': 'gmail.com',
            'hotmail': 'hotmail.com',
            'outlook': 'outlook.com',
            'yahoo': 'yahoo.com',
            'icloud': 'icloud.com'
        }.get(provider.lower())

        if email_domain:
            email_address = f"{username}@{email_domain}"
            emails.append(email_address)
            logging.info(f"Generated email: {email_address}")

        # Update the progress bar
        progress_bar.update(1)

    progress_bar.close()  # Close the progress bar when done

    if skipped_count > 0:
        logging.warning(f"{skipped_count} email(s) skipped due to invalid characters.")

    if not emails:
        logging.warning(f"No valid emails generated for {provider}. Please check your input and try again.")

    return emails, skipped_count

def log_emails(emails, provider, skipped_count):
    """
    Logs the generated email addresses to a file with a timestamp.

    Args:
    emails (list): List of email addresses to be logged.
    provider (str): The email provider.
    skipped_count (int): The count of skipped emails.

    Returns:
    None
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"{provider.lower()}addresses_{timestamp}.txt"

    try:
        with open(log_filename, 'w', encoding='utf-8') as log_file:
            for email in emails:
                log_file.write(email + '\n')

            log_file.write('\n' + CREDIT_SECTION)

        num_logged_emails = len(emails)
        logging.info(f"{num_logged_emails} email(s) logged in {log_filename} for provider {provider}.")
        logging.info(f"{skipped_count} email(s) skipped and not logged.")
        logging.info(f"Emails logged in file: {log_filename}")
        logging.info(CREDIT_SECTION)
        print(f"{num_logged_emails} email(s) generated and logged successfully for provider {provider}.")
        print(f"{skipped_count} email(s) skipped due to invalid characters.")
        print(f"Emails logged in file: {log_filename}")

    except Exception as e:
        logging.error(f"Error while logging emails: {e}")
        print(f"Error while logging emails: {e}. Please check the log file for details.")

def get_user_choice():
    """
    Gets and validates user input for the email address generation menu.

    Returns:
    str: The user's valid choice.
    """
    while True:
        choice = input("Enter your choice (0-6): ")

        if choice.isdigit() and 0 <= int(choice) <= 6:
            return choice
        else:
            logging.warning("Invalid choice. Please enter a valid option (0-6).")
            print("Invalid choice. Please enter a valid option (0-6).")

def get_number_of_emails():
    """
    Gets and validates user input for the number of emails to generate.

    Returns:
    int: The number of emails to generate.
    """
    while True:
        try:
            num_emails = int(input("Enter the number of emails to generate: "))
            if num_emails > 0:
                return num_emails
            else:
                print("Please enter a positive integer.\n")
        except ValueError:
            print("Invalid input. Please enter a valid integer.\n")

def get_include_dot_choice():
    """
    Gets and validates user input for including a dot in the email address.

    Returns:
    bool: True if the user wants to include a dot, False otherwise.
    """
    while True:
        include_dot = input("Do you want to include a dot in the address? (y/n): ").lower()
        if include_dot in ['y', 'n']:
            return include_dot == 'y'
        else:
            print("Invalid choice. Please enter 'y' or 'n'.\n")

def print_menu():
    """
    Prints the Email Address Generator Menu.
    """
    print("\nEmail Address Generator Menu:")
    print("1. Generate Gmail Address")
    print("2. Generate Hotmail Address")
    print("3. Generate Outlook Address")
    print("4. Generate Yahoo Address")
    print("5. Generate iCloud Address")
    print("6. Generate All Addresses")
    print("0. Exit")

def main():
    """
    Main function to run the email address generator program.
    """
    logging.info("Email Address Generator started.")

    print(f"""
  /\\_/\\  
 ( o.o ) 
  > ^ <

********** {FILE_NAME} - Version {VERSION} **********
{WELCOME_MSG}

 Support: {SUPPORT_EMAIL}
 Youtube: {YOUTUBE_CHANNEL}
""")

    while True:
        print_menu()

        choice = get_user_choice()

        if choice == '0':
            logging.info("Exiting the program.")
            print("Exiting the program.")
            break

        if choice in ['1', '2', '3', '4', '5']:
            num_emails = get_number_of_emails()

            provider = {
                '1': 'gmail',
                '2': 'hotmail',
                '3': 'outlook',
                '4': 'yahoo',
                '5': 'icloud'
            }.get(choice)

            include_dot = get_include_dot_choice()

            emails, skipped_count = generate_email(provider, num_emails, include_dot)
            log_emails(emails, provider, skipped_count)

        elif choice == '6':
            num_emails = get_number_of_emails()
            include_dot = get_include_dot_choice()

            skipped_count_total = 0
            for p in ['gmail', 'hotmail', 'outlook', 'yahoo', 'icloud']:
                emails, skipped_count = generate_email(p, num_emails, include_dot)
                log_emails(emails, p, skipped_count)
                skipped_count_total += skipped_count

            logging.info(f"Total skipped emails across all providers: {skipped_count_total}")
            print(f"Total skipped emails across all providers: {skipped_count_total}")

        else:
            print("Invalid choice. Please enter a valid option.\n")

if __name__ == "__main__":
    configure_logging()
    main()
