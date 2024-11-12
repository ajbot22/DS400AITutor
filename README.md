# Cloud Mentor
# AI Tutor Platform

A cloud-based, AI-driven tutoring platform that leverages Google Cloud and GPT-4 to help students learn course content efficiently.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Database Structure](#database-structure)
- [API Endpoints](#api-endpoints)
- [Current Development](#current-development)
- [Future Development](#future-development)
- [License](#license)

## Project Overview
The AI Tutor Platform provides a customized learning experience using AI. It allows proctors to upload course documents, processes them to understand content, and enables students to ask questions on the material.

## Features
- Cloud-based AI tutoring with OpenAI GPT-4
- Google Cloud Integration for file storage and database management
- Secure access and role-based management with PostgreSQL

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/yourrepository.git
    cd yourrepository
    ```
2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Set up environment variables in a `.env` file:
    ```plaintext
    OPENAI_API_KEY=your_openai_api_key
    GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
    DB_HOST=35.196.108.73
    DB_NAME=your_db
    DB_USER=your_user
    DB_PASS=your_password
    ```

## Usage
Run the application:
```bash
  python app.py
 ```
The platform will start on localhost:5000, accessible in your browser.

## Database Structure
The platform includes the following database tables:

- Proctors - Stores proctor ID, email, and password.
- Courses - Stores course information, including name, proctor association, and file paths.
- Students - Stores student information, including usernames and passwords.
- Student_Courses - Links students to their courses and tracks individual learning contexts.

## API Endpoints
- /upload - Upload course materials.
- /train - Process course documents to build an AI model.
- /chat - Interact with the AI tutor.

## Current Development
- Full integration of the PostgreSQL database into the program
- Exploration of Mathematical support
- Test of more variety of models

## Future Development
Add support for new file types
Expand AI model capabilities with interactive and adaptive learning modules
Integrate multi-language support

## License
This project is licensed under the MIT License.
