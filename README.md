# Nest 2 Thermostat Local Controller

This project provides a web-based control panel for "deprecated" or "unsupported" Nest Thermostats (specifically Gen 2, but works for others) that are connected to WiFi but cannot be easily controlled via the modern Google Home app due to migration issues or lack of support.

It uses the unofficial "legacy" Nest API which requires you to extract your authentication tokens from a browser session.

## Features

- View current temperature, humidity, and mode.
- Set target temperature.
- Change HVAC mode (Heat/Cool/Off).
- Mobile-friendly interface (Web App).

## Prerequisites

- Python 3.8+
- The Nest Thermostat must be connected to WiFi.
- You must have a Nest account (migrated or not).

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Credentials

You need to create a `config.json` file.

1. Copy the example file:
   ```bash
   cp config.json.example config.json
   ```

2. **Extract Credentials**:
   This is the tricky part. You need to get your `issue_token` and `cookies` from the Nest website.

   *   Open Google Chrome (or Firefox) on your computer.
   *   Open a **Incognito/Private** window.
   *   Go to [home.nest.com](https://home.nest.com) and log in.
   *   Once logged in, open Developer Tools (Right Click -> Inspect -> Network tab).
   *   Filter by `mobile` or `user`.
   *   Refresh the page.
   *   Look for a request that starts with `user.` (e.g. `user.123456...`).
   *   Click on it and look at the **Request Headers**.
   *   **User ID**: The number in the URL (e.g. `https://transport.home.nest.com/v2/mobile/user.123456`).
   *   **Authorization**: Copy the value starting with `Basic ` and ending there. You need the string *after* `Basic `.
   *   **Cookie**: Copy the entire `Cookie` header string.

3.  **Update `config.json`**:
    Paste the values into the file.
    ```json
    {
      "issue_token": "<YOUR_TOKEN_WITHOUT_BASIC_PREFIX>",
      "cookies": "<YOUR_ENTIRE_COOKIE_STRING>",
      "user_id": "<YOUR_USER_ID>"
    }
    ```

### 3. Run the Server

```bash
python app.py
```

### 4. Control from Phone

1.  Find the IP address of the computer running this script (e.g., `192.168.1.15`).
2.  Open your phone's browser and go to `http://192.168.1.15:5000`.
3.  You should see the control panel!

## Troubleshooting

- **401 Unauthorized**: Your cookies or token have expired. Log in again in the browser and update `config.json`.
- **No devices found**: Ensure your thermostat is actually connected to the Nest account you logged into.

## Disclaimer

This is an unofficial tool and is not affiliated with Google or Nest. Use at your own risk.
