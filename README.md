

# Filtering Hallucinations and Omissions in LLMs Through a Cognitive Architecture

This project aims to filter hallucinations and omissions in Large Language Models (LLMs) using a cognitive architecture. The system integrates ANNABELL, YARP, inotify tools, and LLMs like GPT and Gemini, and is designed to run on Linux.

## Table of Contents
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Starting ANNABELL and YARP](#starting-annabell-and-yarp)
  - [Running Chatbot](#running-chatbot)
  - [Contextual Sentence Search](#contextual-sentence-search)
- [License](#license)

## Installation

To set up the system, follow these steps:

1. **Install ANNABELL**  
   Follow instructions [here](https://github.com/golosio/annabell).

2. **Install YARP**  
   Follow installation details [here](https://www.yarp.it/latest/index.html).

3. **Install inotify-tools**  
   ```bash
   sudo apt-get install inotify-tools
   ```

4. **Install GPT and Gemini APIs**
   - GPT setup: [OpenAI Quickstart](https://platform.openai.com/docs/quickstart)
   - Gemini setup: [Google Gemini Quickstart](https://ai.google.dev/gemini-api/docs/quickstart?lang=python)

## Configuration

1. **Create a `.env` file**  
   Set up the environment variables as shown below, updating paths and keys as needed:

   ```plaintext
   # Google API Key
   API_KEY="your_google_api_key_here"

   # OpenAI API Key
   OPENAI_API_KEY="your_openai_api_key_here"

   # Annabell knowledge path
   KNOWLEDGE_PATH="../annabell/crossvalidation/round1/people/people.txt"

   # Test file path
   TEST_FILE_PATH="../annabell/crossvalidation/round1/people"

   # Read file path
   READ_FILE_PATH="../annabell/annadoc/annabell.txt"

   # Write file path
   WRITE_FILE_PATH="../annabell/annadoc/toAnnabell.txt"
   ```

2. **Modify ANNABELL Makefile**  
   Update `lYARP_OS` to `lYARP_os` in the ANNABELL build folder at `../build/src/Makefile`.

## Usage

### Starting ANNABELL and YARP

1. Start ANNABELL in a terminal:
   ```bash
   annabell
   ```

2. Load the trained data:
   - To load: `.load links_people.txt`
   - To train from data: Use the data source at `crossvalidation/round1/people`

3. (Optional) Run a test file:
   ```bash
   .f test1.txt
   ```

4. Start YARP in a separate terminal:
   ```bash
   yarpserver --write
   ```

5. Make the necessary scripts executable:
   ```bash
   chmod +x readAnnOutput.sh
   chmod +x writeAnnInput.sh
   ```

6. Run the scripts in two different terminals:
   ```bash
   ./readAnnOutput.sh
   ./writeAnnInput.sh
   ```

7. In the ANNABELL terminal, initialize:
   ```bash
   .yo
   .yi
   ```

8. Once all connections are ready, start the chatbot by running `Chat.py` from the `MSC_PROJECT_WORK` directory.

9. To exit the application, type `exit`.

### Contextual Sentence Search

This project includes tools to match user input contextually to test files:

- **TfidfVectorizer**: Implemented in `TextProcessor.py` to retrieve contextually best-matched sentences.
- **BERT**: Implemented in `BERT.py` as an alternative approach for contextual sentence search.

Both files can be run individually for testing purposes, though `BERT.py` is not integrated into the main system.

## License

This project is licensed under the [MIT License](LICENSE).
```

---

This revised version should render correctly on GitHub and in Markdown viewers. Let me know if you need further adjustments!
