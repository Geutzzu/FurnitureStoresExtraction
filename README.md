# Furniture Store Extraction Application
A tool to extract, display and export data about furniture products from any website, built with Django and React and powered by a fine-tuned RoBERTa model for Named Entity Recognition (NER).

1. [Motivation and Overview](#motivation-and-overview)
    1. [Task Overview](#task)
    2. [My approach](#my-approach)

2. [Presentation of Functionality and Features](#features)
    1. [Full demonstration for one link and its subpages](#features)
    2. [How to use](#features)
    3. [Real-time scraping updates using WebSockets](#features)
    4. [Export extracted data as CSV](#features)

3. [Installation and Setup](#installation-and-setup)
    1. [Prerequisites](#prerequisites)
    2. [Backend Setup (Django)](#backend-setup-django)
    3. [Frontend Setup (React)](#frontend-setup-react)
4. [Model Development](#model-development)
    1. [Overview](#overview)
    2. [Model Architecture](#model-architecture)
    3. [Data Collection](#data-collection)
    4. [Training Process](#training-process)
    5. [Model Choices & Justifications](#model-choices-and-justifications)
5. [Backend: Django Server](#backend-django-server)
    1. [Libraries & Tools](#libraries-and-tools)
    2. [WebSocket Integration](#websocket-integration)
    3. [API Endpoints](#api-endpoints)
6. [Frontend: React Client](#frontend-react-client)
    1. [Libraries & Tools](#libraries-and-tools-frontend)
    2. [UI Design](#ui-design)
    3. [State Management & WebSocket Communication](#state-management-and-websocket-communication)
7. [Future Enhancements](#future-enhancements)



# 1. Motivation and Overview


## 1.1 Task Overview

This project was build as a solution to a technical challenge for an internship application. Below is an overview of the task:


### Task:
- Create a new model that is able to extract products from Furniture Stores.
- #### Inputs:
  - A list of URLs from furniture store sites. Most will have products on them, some won’t, some won’t even work at all.
  - The URLs are given inside a CSV file (present in my repo as `furniture stores pages.csv`).
- #### Outputs:
  - A list of product names extracted from every URL alongside other relevant information or insights.


- They also recommend using the Transformer architecture from the sparknlp library or the huggingface transformers library. 

## 1.2 My approach
Important to note is that I did not pick up this 
challenge as a competition or as a way to display my skills.
I took this as a learning opportunity in the world of Machine Learning and NLP. I went blind 
into this challenge, not knowing what difficulties to expect or what the outcome would be. Having
just finished my first year of university (at the time of writing), I am yet to study machine learning formally.
Regardless, I am passionate about the subject and I spent quite a decent amount of time learning about 
this field on my own.

I considered this the perfect task for me to learn how to build a model from scratch 
to solve a real-world problem (and not just some dummy task with a dataset ready for you) and also how 
to integrate it into a full-stack application.

All the difficulties and challenges I faced are documented in their respective sections in this README.
I do feel that covering them could provide a valuable perspective to someone who is just
starting their ML journey (or their software engineering journey in general) and encountered similar problems. 
There was a lot of trial and error,
and a lot of information that is either hard to come by online, or even non-existent.


# 2. Presentation of Functionality and Features

## 2.1 Full demonstration for one link and its subpages

## 2.2 How to use






[//]: # (2. Features)

[//]: # (Extracts furniture data including product images, names, and prices.)

[//]: # (Real-time scraping updates using WebSockets.)

[//]: # (Pagination and dark mode toggle in the frontend.)

[//]: # ([Add more relevant features here])

[//]: # (3. Installation and Setup)

[//]: # (3.1 Prerequisites)

[//]: # (Python 3.8+)

[//]: # (Node.js 14+)

[//]: # ([Add any other dependencies])

[//]: # (3.2 Backend Setup &#40;Django&#41;)

[//]: # (bash)

[//]: # (Copy code)

[//]: # (# Clone the repository)

[//]: # (git clone <your-repo-url>)

[//]: # (cd <backend-directory>)

[//]: # ()
[//]: # (# Install dependencies)

[//]: # (pip install -r requirements.txt)

[//]: # ()
[//]: # (# Run migrations)

[//]: # (python manage.py migrate)

[//]: # ()
[//]: # (# Start Django server)

[//]: # (python manage.py runserver)

[//]: # (Make sure to configure .env file with your own environment variables.)

[//]: # ()
[//]: # (3.3 Frontend Setup &#40;React&#41;)

[//]: # (bash)

[//]: # (Copy code)

[//]: # (# Navigate to frontend directory)

[//]: # (cd <frontend-directory>)

[//]: # ()
[//]: # (# Install dependencies)

[//]: # (npm install)

[//]: # ()
[//]: # (# Start development server)

[//]: # (npm run dev)

[//]: # (4. Model Development)

[//]: # (4.1 Overview)

[//]: # ([Placeholder Text])

[//]: # (Description of the machine learning problem and the chosen approach.)

[//]: # ()
[//]: # (4.2 Model Architecture)

[//]: # ([Placeholder Image/Diagram Placeholder])

[//]: # (Explain the architecture of the model &#40;BERT-like model or other&#41; and how it works. Add details about any layers, embeddings, CRF layer, etc.)

[//]: # ()
[//]: # (4.3 Data Collection)

[//]: # (Source of data &#40;public datasets, web scraping, etc.&#41;)

[//]: # (Preprocessing steps)

[//]: # (4.4 Training Process)

[//]: # (Training configuration &#40;batch size, epochs, optimizer, etc.&#41;)

[//]: # (Validation and test results &#40;metrics&#41;)

[//]: # ([Placeholder for screenshots or training logs])

[//]: # (4.5 Model Choices & Justifications)

[//]: # (Why you chose the specific model.)

[//]: # (Trade-offs considered &#40;e.g., speed vs accuracy&#41;.)

[//]: # (How the model fits the NER problem of identifying furniture products.)

[//]: # (5. Backend: Django Server)

[//]: # (5.1 Libraries & Tools)

[//]: # (Django: Web framework.)

[//]: # (Django Channels: For WebSocket handling.)

[//]: # (REST Framework: For API endpoints.)

[//]: # ([Any other libraries you are using])

[//]: # (5.2 WebSocket Integration)

[//]: # ([Placeholder for technical explanation and diagrams])

[//]: # (How WebSockets are used to provide real-time updates during scraping.)

[//]: # ()
[//]: # (5.3 API Endpoints)

[//]: # ([Placeholder Text])

[//]: # (List and describe the API endpoints exposed by the Django server, including input/output examples.)

[//]: # ()
[//]: # (6. Frontend: React Client)

[//]: # (6.1 Libraries & Tools)

[//]: # (React: UI library.)

[//]: # (Axios: For HTTP requests.)

[//]: # (WebSocket API: For real-time updates.)

[//]: # ([Add others])

[//]: # (6.2 UI Design)

[//]: # ([Placeholder Screenshots of the UI])

[//]: # (Explanation of how the UI is structured and design choices like theming, responsiveness, etc.)

[//]: # ()
[//]: # (6.3 State Management & WebSocket Communication)

[//]: # (How state is handled &#40;with useState, useEffect&#41;.)

[//]: # (WebSocket integration for live updates.)

[//]: # (7. Future Enhancements)

[//]: # ([Placeholder Text])

[//]: # (List potential future improvements or features &#40;e.g., multi-language support, additional data analysis features&#41;.)

[//]: # ()
[//]: # (8. Contributing)

[//]: # ([Placeholder Text])

[//]: # (Guidelines on how to contribute to the project &#40;opening issues, creating pull requests, coding standards, etc.&#41;.)

[//]: # ()
[//]: # (9. License)

[//]: # ([Placeholder Text])

[//]: # (Include the type of license used.)

[//]: # ()
[//]: # ([Insert relevant images or diagrams where needed, including screenshots of the app interface, the model architecture, or system flow diagrams.])