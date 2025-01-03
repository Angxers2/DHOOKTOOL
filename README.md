# Discord Webhook Manager

This Python script provides a set of tools for interacting with Discord webhooks. With this script, you can:
- Send images to webhooks.
- Spam images and text messages to webhooks with configurable delays.
- Create, update, and delete Discord webhooks.
- Retrieve webhook information and manage them effectively.

## Features

- **Send Image to Specific Webhook:** Send an image to a specific webhook URL with an optional accompanying message.
- **Spam Image to All Webhooks:** Repeatedly send the same image to all active webhooks, with a customizable delay between each send.
- **Spam Text Messages to Webhooks:** Send multiple text messages to webhooks at specified intervals.
- **Create Webhook:** Create a webhook in a specified Discord channel using a bot token and channel ID.
- **Update Webhook:** Modify an existing webhook's name or avatar.
- **Delete Webhook:** Delete a specific webhook by URL.
- **Get Webhook Info:** Retrieve detailed information about a webhook, such as the server and channel it is connected to.

## Requirements

- Python 3.x
- `requests` library
- `colorama` library

You can install the required libraries with:

```bash
pip install requests colorama

```

### Windows
1. Download and install Python from [python.org](https://www.python.org/downloads/).
2. Open Command Prompt and install required dependencies:
   ```bash
   pip install requests
   ```
3. Clone or download this repository.
4. Open Command Prompt in the project folder and run the script:
   ```bash
   python webhook_manager.py
   ```

### macOS
1. Install Python via [Homebrew](https://brew.sh/) (if not already installed):
   ```bash
   brew install python
   ```
2. Install required dependencies:
   ```bash
   pip3 install requests
   ```
3. Clone or download this repository.
4. Open Terminal in the project folder and run the script:
   ```bash
   python3 webhook_manager.py
   ```

### Linux (Ubuntu/Debian-based)
1. Install Python and pip:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```
2. Install required dependencies:
   ```bash
   pip3 install requests
   ```
3. Clone or download this repository.
4. Open Terminal in the project folder and run the script:
   ```bash
   python3 webhook_manager.py
   ```

## Usage
Once the script is running, follow the on-screen prompts to send messages, create, update, delete, or retrieve webhooks. Ensure you have the correct webhook URL to interact with the Discord server.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

