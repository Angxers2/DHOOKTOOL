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
