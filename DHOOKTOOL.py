import requests
import time
import os
import base64
from colorama import Fore, Back, Style, init
import json

init(autoreset=True)

active_webhooks = {}

def save_webhooks():
    with open('webhooks.json', 'w') as f:
        json.dump(active_webhooks, f)

def load_webhooks():
    global active_webhooks
    try:
        if os.path.exists('webhooks.json'):
            with open('webhooks.json', 'r') as f:
                active_webhooks = json.load(f)
    except:
        active_webhooks = {}

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def send_image(webhook_url, image_path, message=""):
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
    webhooks_to_use = {name: url for name, url in active_webhooks.items() 
                       if selected_webhooks is None or name in selected_webhooks}
    
    for name, webhook_url in webhooks_to_use.items():
        if send_image(webhook_url, image_path, message):
            print(Fore.GREEN + Style.BRIGHT + f"Image sent to {name}")
        else:
            print(Fore.GREEN + Style.BRIGHT + f"Image sent to {name}")

def spam_image_to_all(image_path, message="", delay=0, selected_webhooks=None):
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
                    if e.response.status_code == 429:
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
    try:
        response = requests.get(url)
        return response.status_code == 200
    except:
        return False

def create_webhook(channel_id, bot_token):
    headers = {
        'Authorization': f'Bot {bot_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'name': 'Created Webhook'
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
    try:
        response = requests.delete(webhook_url)
        if response.status_code == 204:
            print(Fore.GREEN + Style.BRIGHT + "Webhook deleted successfully!")
        else:
            print(Fore.RED + Style.BRIGHT + f"Failed to delete webhook. Status code: {response.status_code}")
    except Exception as e:
        print(Fore.RED + Style.BRIGHT + f"An error occurred: {e}")

def get_webhook_info(webhook_url):
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
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {}
    if new_name:
        payload['name'] = new_name
    if avatar_url:
        try:
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
    webhooks_to_use = {name: url for name, url in active_webhooks.items() 
                       if selected_webhooks is None or name in selected_webhooks}
    
    for name, webhook_url in webhooks_to_use.items():
        try:
            response = requests.post(webhook_url, 
                                  json={"content": message})
            if response.status_code == 204:
                print(Fore.GREEN + Style.BRIGHT + f"Message sent to {name}")
            else:
                print(Fore.RED + Style.BRIGHT + f"Failed to send message to {name}")
        except requests.exceptions.RequestException as e:
            print(Fore.RED + Style.BRIGHT + f"Error sending message to {name}: {e}")

def main():
    clear_screen()
    display_banner()
    load_webhooks()
    
    while True:
        choice = input(Fore.CYAN + Style.BRIGHT + "\nSelect an option:\n1. Send Image\n2. Send Image to All\n3. Spam Image\n4. Manage Webhooks\n5. Exit\n> ")
        
        if choice == '1':
            webhook_name = input(Fore.CYAN + Style.BRIGHT + "Enter the webhook name: ")
            image_path = input(Fore.CYAN + Style.BRIGHT + "Enter the image path: ")
            message = input(Fore.CYAN + Style.BRIGHT + "Enter a message (optional): ")
            if webhook_name in active_webhooks:
                send_image(active_webhooks[webhook_name], image_path, message)
            else:
                print(Fore.RED + Style.BRIGHT + "Webhook name not found.")
        elif choice == '2':
            image_path = input(Fore.CYAN + Style.BRIGHT + "Enter the image path: ")
            message = input(Fore.CYAN + Style.BRIGHT + "Enter a message (optional): ")
            send_image_to_all(image_path, message)
        elif choice == '3':
            image_path = input(Fore.CYAN + Style.BRIGHT + "Enter the image path: ")
            message = input(Fore.CYAN + Style.BRIGHT + "Enter a message (optional): ")
            delay = float(input(Fore.CYAN + Style.BRIGHT + "Enter delay between spams (seconds): "))
            spam_image_to_all(image_path, message, delay)
        elif choice == '4':
            manage_webhooks()
        elif choice == '5':
            break
        else:
            print(Fore.RED + Style.BRIGHT + "Invalid option. Try again.")

if __name__ == "__main__":
    main()
