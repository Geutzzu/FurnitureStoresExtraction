# Furniture Store Extraction Application
A tool to extract, display and export data about furniture products from any website, built with Django and React and powered by a fine-tuned RoBERTa model for Named Entity Recognition (NER).

<details>
  <summary>Table of Contents</summary>

  1. [Presentation of Functionality and Features](#features)
      1. [Full demonstration for one link and its subpages](#features)
      2. [How to use](#features)
      3. [Real-time scraping and inference updates using WebSockets](#features)
      4. [Results Table](#features)
  2. [Motivation and Overview](#motivation-and-overview)
      1. [Task Overview](#task)
      2. [My approach](#my-approach)

  3. [Installation and Setup](#installation-and-setup)
      1. [Prerequisites and Additional Downloads](#prerequisites-and-additional-downloads)
      2. [Frontend Setup (React)](#frontend-setup-react)
      3. [Backend Setup (Django)](#backend-setup-django)
      4. [Notebooks Setup](#notebooks-setup)
  
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

</details>

# 1. Presentation of Functionality and Features

## 1.1. Full demonstration for one link and its subpages

![Dem.gif](ForReadme%2FDem.gif)

## 1.2. How to use
A short guide on how to use the application is also present in dropdown menu of the user interface.
In short, you can:
- Paste a link to a furniture store page in the input field or upload a CSV file 
with multiple links present on the first column (note that
all the following options for extraction will apply to all the links in the CSV file).
- Choose if you want to search the subpages of the link for products as well.
- If you chose to search the subpages, you can also choose what paths the urls should contain (if what you search
for contains /products/ in the URL for example).
- If you entered a sitemap (with the .xml extension), you can choose the XML tag to search for (loc is the most commonly used).
- After the scraping and inference is done, you can export the data as a CSV file with the click of a button.

Please note that the application is intended for desktop use only, and the UI is not optimized for other devices.
Also, the application as it stands is intended for running locally only, and not for deployment on a server.

## 1.3. Real-time scraping and inference updates using WebSockets
Over the course of the process, you can see progress updates in real time through WebSockets.

One thing to note here, is that for scraping pages with a lot of matching links, the progress bar
may not update that frequently (since it waits for the scraping of all the links from one recursion level before updating).

Do not refresh the page while the process is ongoing, as you will no longer get UI updates from the backend.
If you think the process is taking too long, you can always check the console to see the progress or 
to kill the backend if needed (assuming you are running the application locally).

![img.png](ForReadme/img_status.png)

## 1.4. Results Table
After the scraping process is done, you will start to see the results from each link appear in the table.
You can also scroll through all the pages at the same time as new products are being computed and added to the table.

The table will contain the following collumns:
- Images scraped from the page where the product was found (using a rule-based approach and not a model).
- The name of the product found on the page (extracted by the model).
- The price of the product found on the page (extracted using a rule-based approach).
- The link to the page where the product was found.

A known issue is that you cannot scroll through the images from a product in the table while inference is ongoing,
as the images are not stored in any database and the table is rendered each time a new product is found.
The images are actually displayed using the src attribute of an img tag, so they are not stored in memory either.
 
![img_1.png](ForReadme/img_table.png)

# 2. Motivation and Overview


## 2.1. Task Overview

This project was build as a solution to a technical challenge for an internship application. Below is an overview of the task:
### Task:
- Create a new model that is able to extract products from Furniture Stores.
- #### Inputs:
  - A list of URLs from furniture store sites. Most will have products on them, some won’t, some won’t even work at all.
  - The URLs are given inside a CSV file (present in my repo as `furniture stores pages.csv`).
- #### Outputs:
  - A list of product names extracted from every URL alongside other relevant information or insights.


- They also recommend using the Transformer architecture from the sparknlp library or the huggingface transformers library. 

## 2.2. My approach
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




# 3. Installation and Setup

## 3.1. Prerequisites and Additional Downloads
- The backend and notebooks were built using Python 3.12 (but should work with python 3.10+ as well).
- The frontend was built using Node.js v20.15.0 (but should work with any relatively recent version of Node.js).
- Any modern web browser (Chrome, Firefox, Edge, etc.).

After you have all of the above, you can clone the repository using the following command:
```bash
git clone https://github.com/Geutzzu/FurnitureStoresExtraction.git
```
The repository contains three main directories:
1. Client: contains the frontend code.
2. Server: contains the backend code (without the model since its too large).
3. ModelDevelopment: contains the notebooks used for model development (and some CSV files
that were small enough to be uploaded to GitHub).

   
## 3.2. Frontend Setup (React)
- To install the frontend dependencies using node when loading for the first time you have to:
  #### 1. Navigate to the client directory:
     ```bash
     cd client
     ```
  #### 2. Install the dependencies:
     ```bash
      npm install
     ```
- Then, whenever you want to start the development server, you can run this from the client directory:
     ```bash
     npm run dev
     ```
- If everything went well you should see the following when running:
![img.png](ForReadme/img.png)

## 3.3. Backend Setup (Django)
- To install the backend dependencies using pip when loading for the first time you have to:
  #### 1. Navigate to the django app directory:
     ```bash
     cd server/mlbackend
     ```
  #### 2. Set up a virtual environment if you don't have one (exactly the same as in the notebooks setup):
     ```bash
     python -m venv .venv
     ```
  #### 3. Activate the virtual environment:
     - On Windows:
       ```bash
       .venv\Scripts\activate
       ```
     - On Linux/Mac:
       ```bash
       source .venv/bin/activate
       ```
    #### 4. Install the dependencies:
     ```bash
    pip install -r requirements.txt
     ``` 
- After this, you will have to create a directory called `Models` (if it does not exist) in the `FurnitureFinder` directory
  (where the django app is located).
- You can then download one of my trained models from the google drive link below, and add it to the `Models` directory:
  - [ROB_0.89F1_16B_100000DAT](https://drive.google.com/drive/folders/1kuXdzfuZpfyJGMZYohPATBuOGeN6lxTz?usp=sharing)
- For the model above, the app will work plug-and-play. If you want to use a different model, you will have to
change the model path in the `inference.py` file in the `Scripts` directory inside the django app.
    ```py
    # load the model and tokenizer
    model_name = model_checkpoint = "MlBackend/FurnitureFinder/Models/ROB_0.89F1_16B_100000DAT"
    ```


- Then, to start the server using daphne, you can do so by running the following command (from the same directory):
     ````bash
     daphne -p 8000 MlBackend.asgi:application 
     ````
- If everything went well you should see the following when running:
  ![img_1.png](ForReadme/img_1.png)
- NOTE: The WebSocket connection will not work unless you refresh
the page after the server is started. If it is connected you will see this:
![img_2.png](ForReadme/img_2.png)

## 3.4. Notebooks Setup
- The notebooks were also built using Python 3.12. You can create a virtual environment using the exact same steps
as above in the following directory:
  ```bash
  cd ModelDevelopment
  ```
- If you want all the dependencies (although you can just install them as you go through the notebooks),
you can install them using the following command from that same directory:
  ```bash
  pip install -r requirements.txt
  ```
- NOTE: I did experience some issues using the `requirements.txt` file in pycharm due to the kernel
not being able to find the dependencies (although when checking for them via the terminal they are there). 
This did not bother me personally much since pycharm allows you to install
dependencies directly from the IDE. If installing through the IDE did not work, pip installing them manually in
your project should work just fine.



