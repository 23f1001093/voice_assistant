# AI Voice Assistant - Production Model

This project contains the source code for a scalable, production-ready AI voice assistant on Telegram, built using the "Private Group Call Method".

## Architecture

This service is built on a distributed, cloud-native architecture designed for scalability and reliability. It leverages Telegram's Group Voice Chat API to provide private, 1-on-1 live call sessions.

- **Frontend:** A standard Telegram Bot (`@YourAIBot`) serves as the user-facing entry point.
- **Backend:** A pool of containerized Python "workers" manages live sessions. Each worker handles a single session in an isolated environment.
- **Infrastructure:** Designed for deployment on cloud platforms like AWS, GCP, or Azure, using Kubernetes for orchestration.

## Features

- **Massive Scalability:** Can handle hundreds or thousands of simultaneous private calls.
- **Zero Telecom Costs:** Operates entirely over the internet using Telegram's free APIs.
- **High Reliability:** Deployed in a cloud environment for 24/7 uptime.
- **Compliance:** Adheres to Telegram's ToS by using official APIs.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd ai-voice-assistant
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment:**
    -   Copy `.env.example` to a new file named `.env`.
    -   Fill in your `API_ID`, `API_HASH`, and `BOT_TOKEN`.

5.  **Run the application:**
    ```bash
    python main.py
    ```

## Usage

1.  Start a private chat with your bot on Telegram.
2.  Send the `/start` command.
3.  Send the `/session` command to initiate a private live call.
