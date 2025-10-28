# Llama Languages AI Practice Platform

Llama Languages is a self-hosted, AI-powered application designed for immersive language practice. It allows you to engage in real-time, spoken or written conversations with customizable AI personas, receiving instant feedback on grammar, style, and pronunciation.

This project is built for language learners who want a private, configurable, and endlessly patient practice partner.

## Screenshots

**Conversation Interface:**
<img width="1675" height="920" alt="image" src="https://github.com/user-attachments/assets/703fef31-4dea-4426-ba34-dc723e38c7f8" />

**Conversation Interface w/ Feedbacks:**
<img width="1186" height="786" alt="image" src="https://github.com/user-attachments/assets/ce2fe72a-3e34-4473-93f1-1873d724b992" />

**Language Profiles:**
<img width="1689" height="911" alt="image" src="https://github.com/user-attachments/assets/4e7116f4-35ca-4b75-b286-fc09b49cec10" />

**Settings Page:**
<img width="1745" height="931" alt="image" src="https://github.com/user-attachments/assets/f6c5f20b-0343-4229-a66b-d0d7f8c2f367" />

**Create Persona:**
<img width="1680" height="914" alt="image" src="https://github.com/user-attachments/assets/61cf256a-daf2-4811-a4d6-0a9e696784de" />


## Core Features

*   **AI-Powered Conversations**: Engage in dynamic, open-ended conversations with an AI tutor powered by Google's Gemini models.
*   **Voice and Text Input**: Practice by speaking through your microphone or typing your messages. The application provides real-time transcription for voice input.
*   **Real-time Audio Responses**: Hear the AI's responses streamed back to you in a natural-sounding voice, powered by ElevenLabs TTS.
*   **Instant, Actionable Feedback**: After each message you send, the AI analyzes your input and provides concise feedback on corrections, suggestions, and pronunciation.
*   **Customizable Personas**: Define the personality, background, and speaking style of your AI practice partner. The application comes with several pre-built personas, from a nurturing beginner's guide to a cynical cyberpunk citizen.
*   **Structured Language Profiles**: Create dedicated profiles for each language you're learning. Assign a persona and create custom practice topics (e.g., "Spanish A2 Grammar," "Ordering at a French Restaurant").
*   **Self-Hostable and Private**: Run the application on your own machine. Your API keys and conversation history stay with you.
*   **Highly Configurable**: Through a simple web interface, you can configure your API keys, select different LLM models for different tasks (e.g., transcription vs. feedback), and adjust parameters like temperature to fine-tune the AI's behavior.

## Technology Stack

*   **Backend**: Python, FastAPI
*   **Frontend**: HTMX, Alpine.js, Tailwind CSS
*   **AI/LLM**: Google Gemini (integrated via `llama-index`)
*   **Text-to-Speech (TTS)**: ElevenLabs
*   **Database**: SQLAlchemy (defaults to SQLite)
*   **Async Workflow Management**: `workflows` (llama-index)

## Getting Started

Follow these steps to get the application running on your local machine.

### Prerequisites

*   Python 3.11+
*   [uv](https://github.com/astral-sh/uv)
*   Git

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/marcius-llmus/llama-languages.git
    cd llama-languages
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    uv sync
    ```

4.  **Set up your environment variables:**
    The application uses a local SQLite database by default, which will be created at the root of the project. No environment variables are needed to get started. The API keys for Gemini and ElevenLabs can be configured later in the web UI.
    
5.  **Run database migrations:**
    This will create the necessary tables in your database.
    ```bash
    alembic upgrade head
    ```

6.  **Start the application:**
    ```bash
    uvicorn app.main:app --reload
    ```

7.  **Access the application:**
    Open your web browser and navigate to `http://localhost:8010` (or `http://127.0.0.1:8010`). You will be redirected to the Personas page.

### Running with Docker

Alternatively, you can run the application using Docker for a more isolated setup.

*   Docker
*   Git

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/marcius-llmus/llama-languages.git
    cd llama-languages
    ```

2.  **Build and Run the Container:**
    ```bash
    docker build -t llama-languages . && docker run --rm -p 8010:8010 -v $(pwd)/data:/app/data llama-languages
    ```
    This command first builds the image and then, upon success, runs the container. The flags for the `run` command are:
    *   `--rm`: Automatically removes the container when it exits.
    *   `-p 8010:8010`: Maps port 8010 on your host to port 8010 in the container.
    *   `-v $(pwd)/data:/app/data`: Mounts the local `data` directory into the container to persist the database.

3.  **Access the application:**
    Open your web browser and navigate to `http://localhost:8010` (or `http://127.0.0.1:8010`).

## Configuration and Usage

The first time the application runs, it automatically seeds the database with a set of default personas and language profiles to get you started.

### Step 1: Configure Settings

1.  Navigate to the **Settings** page from the top navigation bar.
2.  Enter your **Gemini API Key** and **ElevenLabs API Key**.
3.  Find a **Voice ID** from your ElevenLabs account that you'd like to use and enter it.
4.  Review the other settings. For beginners, the defaults are fine.
5.  Click **Save Settings** (Currently, there is no feedback on save, but a click saves).

### Step 2: Create a Language Profile

1.  Navigate to the **Language Profiles** page.
2.  Fill out the "Create New Profile" form:
    *   **Profile Name**: A descriptive name (e.g., "Conversational Spanish").
    *   **Target Language**: The language you want to practice (e.g., "Spanish").
    *   **Practice Persona**: Select one of the pre-configured AI personas.
3.  Click **+ Create Profile**.

### Step 3: Add Practice Topics (Optional)

Within your newly created Language Profile, you can add specific topics to guide your practice sessions.

*   Enter a topic name (e.g., "The Verb 'Ser' vs. 'Estar'") and click **+ Add Topic**.
*   When you start a session, you can select one of these topics from a dropdown menu. If you don't select one, the conversation will be open-ended.

### Step 4: Start Practicing!

1.  On the Language Profiles page, find the profile you want to use and click the green **Practice** button.
2.  You will be taken to the conversation interface.
3.  To send a message:
    *   **Type** your message in the input box and press Enter or click the send button.
    *   **Speak** by clicking the microphone icon. Click it again to stop recording and send the audio.
4.  Wait for the AI to respond with text and audio, and review the feedback provided on your message.

## Project Architecture

The project follows a clean, modular architecture to separate concerns, making it maintainable and extensible.

*   **Application-Based Structure**: Code is organized by features (e.g., `app/personas`, `app/settings`).
*   **Service Layer**: Contains all pure business logic, decoupled from the web layer. It orchestrates the application's core functionalities.
*   **Repository Pattern**: The data access layer is managed by repositories, which mediate between the service layer and the database.
*   **HTMX Frontend**: The frontend is rendered on the server and made dynamic using HTMX, minimizing the need for complex client-side JavaScript.
*   **API Boundary**:
    *   `routes/htmx.py`: Handles all routes that render HTML for the user interface.
    *   `routes/api.py` (if present): Would handle all routes that return JSON for machine-to-machine communication.

## Contributing

Contributions are welcome! If you have ideas for new features, bug fixes, or improvements, please feel free to:

1.  Open an issue to discuss the proposed changes.
2.  Fork the repository and create a pull request with your contributions.

Please ensure that your code adheres to the project's formatting and linting standards by running the provided scripts:
```bash
./scripts/format.sh
./scripts/lint.sh
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
