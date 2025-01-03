import time
import os
import base64
from colorama import Fore, Back, Style, init
import json
import requests

# Initialize Colorama
init(autoreset=True)

# Global storage for webhooks
active_webhooks = {}

def save_webhooks():
    """Saves webhooks to a file"""
    with open('webhooks.json', 'w') as f:
        json.dump(active_webhooks, f)

def load_webhooks():
    """Loads webhooks from file"""
    global active_webhooks
    try:
        if os.path.exists('webhooks.json'):
            with open('webhooks.json', 'r') as f:
                active_webhooks = json.load(f)
    except:
        active_webhooks = {}

def clear_screen():
    """Clears the terminal screen based on the operating system"""
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For Unix/Linux/MacOS
        os.system('clear')

def send_image(webhook_url, image_path, message=""):
    """Sends an image to a webhook with optional message"""
    try:
        with open(image_path, 'rb') as image:
            files = {
                'file': (image_path.split('/')[-1], image),
            }
            payload = {}
            if message:
                payload['content'] = message
                
            response = requests.post(
                webhook_url,
                data=payload,
                files=files
            )
            
            return response.status_code == 204
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"Error sending image: {e}")
        return False

def send_image_to_all(image_path, message="", selected_webhooks=None):
    """Sends an image to selected webhooks or all webhooks"""
    webhooks_to_use = {name: url for name, url in active_webhooks.items() 
                       if selected_webhooks is None or name in selected_webhooks}
    
    for name, webhook_url in webhooks_to_use.items():
        if send_image(webhook_url, image_path, message):
            print(Fore.GREEN + Style.BRIGHT + f"Image sent to {name}")
        else:
            print(Fore.GREEN + Style.BRIGHT + f"Image sent to {name}")

def spam_image_to_all(image_path, message="", delay=0, selected_webhooks=None):
    """Spams an image to selected webhooks or all webhooks"""
    webhooks_to_use = {name: url for name, url in active_webhooks.items() 
                       if selected_webhooks is None or name in selected_webhooks}
    
    while True:
        try:
            for name, webhook_url in webhooks_to_use.items():
                try:
                    if send_image(webhook_url, image_path, message):
                        print(Fore.GREEN + Style.BRIGHT + f"Image sent to {name}")
                    else:
                        print(Fore.GREEN + Style.BRIGHT + f"Image sent to {name}")
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:  # Rate limit
                        retry_after = e.response.json().get("retry_after", 1)
                        print(Fore.YELLOW + Style.BRIGHT + f"Rate limited on {name}. Waiting {retry_after}s")
                        time.sleep(retry_after)
                except Exception as e:
                    print(Fore.RED + Style.BRIGHT + f"Error sending to {name}: {e}")
            time.sleep(delay)
        except KeyboardInterrupt:
            print(Fore.YELLOW + Style.BRIGHT + "\nStopping image spam...")
            break

def is_valid_webhook_url(url):
    """Validates if the given URL is a valid Discord webhook URL"""
    try:
        response = requests.get(url)
        return response.status_code == 200
    except:
        return False

def create_webhook(channel_id, bot_token):
    """Creates a new webhook in the specified channel"""
    headers = {
        'Authorization': f'Bot {bot_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'name': 'Created Webhook'  # Default name, can be changed later
    }
    
    try:
        response = requests.post(
            f'https://discord.com/api/v10/channels/{channel_id}/webhooks',
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            webhook_data = response.json()
            webhook_url = f"https://discord.com/api/webhooks/{webhook_data['id']}/{webhook_data['token']}"
            active_webhooks[webhook_data['name']] = webhook_url
            save_webhooks()
            print(Fore.GREEN + Style.BRIGHT + f"Webhook created successfully!")
            print(Fore.GREEN + Style.BRIGHT + f"Webhook URL: {webhook_url}")
            return webhook_url
        else:
            print(Fore.RED + Style.BRIGHT + f"Failed to create webhook. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"An error occurred: {e}")
        return None

def delete_webhook(webhook_url):
    """Deletes a webhook using its URL"""
    try:
        response = requests.delete(webhook_url)
        if response.status_code == 204:
            print(Fore.GREEN + Style.BRIGHT + "Webhook deleted successfully!")
        else:
            print(Fore.RED + Style.BRIGHT + f"Failed to delete webhook. Status code: {response.status_code}")
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"An error occurred: {e}")

def get_webhook_info(webhook_url):
    """Retrieves information about a webhook"""
    try:
        response = requests.get(webhook_url)
        if response.status_code == 200:
            webhook_info = response.json()
            print(Fore.GREEN + Style.BRIGHT + "\nWebhook Information:")
            print(Fore.YELLOW + Style.BRIGHT + f"Name: {webhook_info['name']}")
            print(Fore.YELLOW + Style.BRIGHT + f"Channel ID: {webhook_info['channel_id']}")
            print(Fore.YELLOW + Style.BRIGHT + f"Guild ID: {webhook_info['guild_id']}")
            print(Fore.YELLOW + Style.BRIGHT + f"Token: {webhook_info['token']}")
            return webhook_info
        else:
            print(Fore.RED + Style.BRIGHT + f"Failed to get webhook info. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"An error occurred: {e}")
        return None

def update_webhook(webhook_url, new_name=None, avatar_url=None):
    """Updates a webhook's name and/or avatar"""
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {}
    if new_name:
        payload['name'] = new_name
    if avatar_url:
        try:
            # Get avatar image and convert to base64
            avatar_response = requests.get(avatar_url)
            if avatar_response.status_code == 200:
                avatar_base64 = base64.b64encode(avatar_response.content).decode('utf-8')
                payload['avatar'] = f"data:image/png;base64,{avatar_base64}"
        except Exception as e:
            print(Fore.RED + Style.BRIGHT + f"Failed to process avatar image: {e}")
    
    try:
        response = requests.patch(webhook_url, headers=headers, json=payload)
        if response.status_code == 200:
            print(Fore.GREEN + Style.BRIGHT + "Webhook updated successfully!")
        else:
            print(Fore.RED + Style.BRIGHT + f"Failed to update webhook. Status code: {response.status_code}")
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"An error occurred: {e}")

def get_server_info(webhook_url):
    """Gets information about the server using the webhook"""
    try:
        response = requests.get(webhook_url)
        if response.status_code == 200:
            webhook_info = response.json()
            guild_id = webhook_info['guild_id']
            channel_id = webhook_info['channel_id']
            
            print(Fore.GREEN + Style.BRIGHT + "\nServer Information:")
            print(Fore.YELLOW + Style.BRIGHT + f"Guild ID: {guild_id}")
            print(Fore.YELLOW + Style.BRIGHT + f"Channel ID: {channel_id}")
            print(Fore.YELLOW + Style.BRIGHT + f"Server Name: {webhook_info.get('guild', {}).get('name', 'N/A')}")
            return webhook_info
        else:
            print(Fore.RED + Style.BRIGHT + f"Failed to get server info. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"An error occurred: {e}")
        return None

def display_banner():
    banner = '''
·▄▄▄▄   ▄ .▄            ▄ •▄ ▄▄▄▄▄            ▄▄▌  
██▪ ██ ██▪▐█▪     ▪     █▌▄▌▪•██  ▪     ▪     ██•  
▐█· ▐█▌██▀▐█ ▄█▀▄  ▄█▀▄ ▐▀▀▄· ▐█.▪ ▄█▀▄  ▄█▀▄ ██▪  
██. ██ ██▌▐▀▐█▌.▐▌▐█▌.▐▌▐█.█▌ ▐█▌·▐█▌.▐▌▐█▌.▐▌▐█▌▐▌
▀▀▀▀▀• ▀▀▀ · ▀█▄▀▪ ▀█▄▀▪·▀  ▀ ▀▀▀  ▀█▄▀▪ ▀█▄▀▪.▀▀▀
    '''
    print(Fore.CYAN + Style.BRIGHT + banner)
    if active_webhooks:
        print(Fore.RED + Style.BRIGHT + "Targets:")
        for name, url in active_webhooks.items():
            print(Fore.RED + Style.BRIGHT + f"- {name}")

def send_message_to_all(message, selected_webhooks=None):
    """
    Sends a message to selected webhooks or all webhooks
    selected_webhooks: list of webhook names to send to, if None sends to all
    """
    webhooks_to_use = {name: url for name, url in active_webhooks.items() 
                       if selected_webhooks is None or name in selected_webhooks}
    
    for name, webhook_url in webhooks_to_use.items():
        try:
            response = requests.post(webhook_url, 
                                  json={'content': message}, 
                                  headers={'Content-Type': 'application/json'})
            if response.status_code == 204:
                print(Fore.GREEN + Style.BRIGHT + f"Message sent to {name}")
            else:
                print(Fore.RED + Style.BRIGHT + f"Failed to send to {name}")
        except Exception as e:
            print(Fore.RED + Style.BRIGHT + f"Error sending to {name}: {e}")

def spam_all_webhooks(message, delay, selected_webhooks=None):
    """
    Spams selected webhooks or all webhooks
    selected_webhooks: list of webhook names to spam, if None spams all
    """
    webhooks_to_use = {name: url for name, url in active_webhooks.items() 
                       if selected_webhooks is None or name in selected_webhooks}
    
    while True:
        try:
            for name, webhook_url in webhooks_to_use.items():
                try:
                    response = requests.post(webhook_url, 
                                          json={'content': message}, 
                                          headers={'Content-Type': 'application/json'})
                    if response.status_code == 204:
                        print(Fore.GREEN + Style.BRIGHT + f"Message sent to {name}")
                    elif response.status_code == 429:  # Rate limit
                        retry_after = response.json().get("retry_after", 1)
                        print(Fore.YELLOW + Style.BRIGHT + f"Rate limited on {name}. Waiting {retry_after}s")
                        time.sleep(retry_after)
                    else:
                        print(Fore.RED + Style.BRIGHT + f"Failed to send to {name}")
                except Exception as e:
                    print(Fore.RED + Style.BRIGHT + f"Error sending to {name}: {e}")
            time.sleep(delay)
        except KeyboardInterrupt:
            print(Fore.YELLOW + Style.BRIGHT + "\nStopping spam...")
            break

def select_webhooks():
    """Helper function to select webhooks from the available ones"""
    if not active_webhooks:
        print(Fore.RED + Style.BRIGHT + "No webhooks available!")
        return None
        
    print(Fore.YELLOW + Style.BRIGHT + "\nAvailable webhooks:")
    for i, (name, _) in enumerate(active_webhooks.items(), 1):
        print(f"{i}. {name}")
    
    print(Fore.YELLOW + Style.BRIGHT + f"{len(active_webhooks) + 1}. All webhooks")
    
    try:
        choice = int(input(Fore.CYAN + Style.BRIGHT + "Choose webhook number: ").strip())
        if choice == len(active_webhooks) + 1:
            return None  # None means all webhooks
        elif 1 <= choice <= len(active_webhooks):
            return [list(active_webhooks.keys())[choice - 1]]  # Return list with single webhook name
        else:
            print(Fore.RED + Style.BRIGHT + "Invalid selection!")
            return None
    except ValueError:
        print(Fore.RED + Style.BRIGHT + "Invalid input!")
        return None

def main():
    load_webhooks()
    while True:
        clear_screen()
        display_banner()
        print(Fore.BLUE + Style.BRIGHT + "\nDiscord Webhook Management Tool")
        print(Fore.YELLOW + Style.BRIGHT + "1. Send a Single Message (All Webhooks)")
        print(Fore.YELLOW + Style.BRIGHT + "2. Spam Messages (All Webhooks)")
        print(Fore.YELLOW + Style.BRIGHT + "3. Add Existing Webhook")
        print(Fore.YELLOW + Style.BRIGHT + "4. Create New Webhook")
        print(Fore.YELLOW + Style.BRIGHT + "5. Delete Webhook")
        print(Fore.YELLOW + Style.BRIGHT + "6. Get Webhook Info")
        print(Fore.YELLOW + Style.BRIGHT + "7. Update Webhook (Name and Avatar)")
        print(Fore.YELLOW + Style.BRIGHT + "8. Get Server Info")
        print(Fore.YELLOW + Style.BRIGHT + "9. Clear All Webhooks")
        print(Fore.YELLOW + Style.BRIGHT + "10. Send Single Image (All Webhooks)")
        print(Fore.YELLOW + Style.BRIGHT + "11. Spam Images (All Webhooks)")
        
        try:
            choice = int(input(Fore.CYAN + Style.BRIGHT + "\nChoose an option: ").strip())
            
            if choice == 1:
                message = input(Fore.CYAN + Style.BRIGHT + "Enter the message to send: ").strip()
                send_message_to_all(message)
            
            elif choice == 2:
                message = input(Fore.CYAN + Style.BRIGHT + "Enter the message to spam: ").strip()
                try:
                    delay_input = input(Fore.CYAN + Style.BRIGHT + "Enter delay between messages (seconds, default 0): ").strip()
                    delay = float(delay_input) if delay_input else 0
                except ValueError:
                    print(Fore.RED + Style.BRIGHT + "Invalid delay. Using 0 seconds.")
                    delay = 0
                spam_all_webhooks(message, delay)
            
            elif choice == 3:
                webhook_url = input(Fore.CYAN + Style.BRIGHT + "Enter webhook URL: ").strip()
                if is_valid_webhook_url(webhook_url):
                    response = requests.get(webhook_url)
                    webhook_info = response.json()
                    active_webhooks[webhook_info['name']] = webhook_url
                    save_webhooks()
                    print(Fore.GREEN + Style.BRIGHT + "Webhook added successfully!")
                else:
                    print(Fore.RED + Style.BRIGHT + "Invalid webhook URL!")
            
            elif choice == 4:
                channel_id = input(Fore.CYAN + Style.BRIGHT + "Enter channel ID: ").strip()
                bot_token = input(Fore.CYAN + Style.BRIGHT + "Enter bot token: ").strip()
                create_webhook(channel_id, bot_token)
            
            elif choice == 5:
                if not active_webhooks:
                    print(Fore.RED + Style.BRIGHT + "No webhooks to delete!")
                    continue
                    
                print(Fore.YELLOW + Style.BRIGHT + "\nAvailable webhooks:")
                for i, (name, _) in enumerate(active_webhooks.items(), 1):
                    print(f"{i}. {name}")
                    
                try:
                    idx = int(input(Fore.CYAN + Style.BRIGHT + "Enter webhook number to delete: ").strip()) - 1
                    name = list(active_webhooks.keys())[idx]
                    webhook_url = active_webhooks[name]
                    delete_webhook(webhook_url)
                    del active_webhooks[name]
                    save_webhooks()
                except (IndexError, ValueError):
                    print(Fore.RED + Style.BRIGHT + "Invalid selection!")
            
            elif choice == 6:
                if not active_webhooks:
                    print(Fore.RED + Style.BRIGHT + "No webhooks available!")
                    continue
                    
                print(Fore.YELLOW + Style.BRIGHT + "\nAvailable webhooks:")
                for i, (name, url) in enumerate(active_webhooks.items(), 1):
                    print(f"{i}. {name}")
                    
                try:
                    idx = int(input(Fore.CYAN + Style.BRIGHT + "Enter webhook number: ").strip()) - 1
                    name = list(active_webhooks.keys())[idx]
                    webhook_url = active_webhooks[name]
                    get_webhook_info(webhook_url)
                except (IndexError, ValueError):
                    print(Fore.RED + Style.BRIGHT + "Invalid selection!")

            elif choice == 7:
                if not active_webhooks:
                    print(Fore.RED + Style.BRIGHT + "No webhooks available!")
                    continue
                    
                print(Fore.YELLOW + Style.BRIGHT + "\nAvailable webhooks:")
                for i, (name, url) in enumerate(active_webhooks.items(), 1):
                    print(f"{i}. {name}")
                    
                try:
                    idx = int(input(Fore.CYAN + Style.BRIGHT + "Enter webhook number: ").strip()) - 1
                    name = list(active_webhooks.keys())[idx]
                    webhook_url = active_webhooks[name]
                    new_name = input(Fore.CYAN + Style.BRIGHT + "Enter new name (or press Enter to skip): ").strip()
                    avatar_url = input(Fore.CYAN + Style.BRIGHT + "Enter avatar URL (or press Enter to skip): ").strip()
                    if new_name or avatar_url:
                        update_webhook(webhook_url, new_name if new_name else None, avatar_url if avatar_url else None)
                except (IndexError, ValueError):
                    print(Fore.RED + Style.BRIGHT + "Invalid selection!")

            elif choice == 8:
                if not active_webhooks:
                    print(Fore.RED + Style.BRIGHT + "No webhooks available!")
                    continue
                    
                print(Fore.YELLOW + Style.BRIGHT + "\nAvailable webhooks:")
                for i, (name, url) in enumerate(active_webhooks.items(), 1):
                    print(f"{i}. {name}")
                    
                try:
                    idx = int(input(Fore.CYAN + Style.BRIGHT + "Enter webhook number: ").strip()) - 1
                    name = list(active_webhooks.keys())[idx]
                    webhook_url = active_webhooks[name]
                    get_server_info(webhook_url)
                except (IndexError, ValueError):
                    print(Fore.RED + Style.BRIGHT + "Invalid selection!")

            elif choice == 9:
                active_webhooks.clear()
                save_webhooks()
                print(Fore.GREEN + Style.BRIGHT + "All webhooks cleared!")
            
            elif choice == 10:
                image_path = input(Fore.CYAN + Style.BRIGHT + "Enter the path to the image: ").strip()
                if not os.path.exists(image_path):
                    print(Fore.RED + Style.BRIGHT + "Image file not found!")
                    continue
                message = input(Fore.CYAN + Style.BRIGHT + "Enter optional message (or press Enter to skip): ").strip()
                selected = select_webhooks()
                send_image_to_all(image_path, message, selected)

            elif choice == 11:
                image_path = input(Fore.CYAN + Style.BRIGHT + "Enter the path to the image: ").strip()
                if not os.path.exists(image_path):
                    print(Fore.RED + Style.BRIGHT + "Image file not found!")
                    continue
                message = input(Fore.CYAN + Style.BRIGHT + "Enter optional message (or press Enter to skip): ").strip()
                try:
                    delay_input = input(Fore.CYAN + Style.BRIGHT + "Enter delay between messages (seconds, default 0): ").strip()
                    delay = float(delay_input) if delay_input else 0
                except ValueError:
                    print(Fore.RED + Style.BRIGHT + "Invalid delay. Using 0 seconds.")
                    delay = 0
                selected = select_webhooks()
                spam_image_to_all(image_path, message, delay, selected)

            input("\nPress Enter to continue...")
            
        except ValueError:
            print(Fore.RED + Style.BRIGHT + "Invalid input. Please enter a number.")
            input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            print(Fore.RED + Style.BRIGHT + "\nExiting the program...")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + Style.BRIGHT + "\nExiting the program...")