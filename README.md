# EcoPulse

EcoPulse is a waste management tracker designed to help small businesses reduce their environmental impact and save money. By tracking waste patterns, the app provides actionable insights that promote sustainable business practices and operational efficiency.

Architecture

user.py — The primary module of the application. This file contains the Streamlit frontend, handles user input, and processes all core business logic for waste tracking and data visualization.

waste_log.csv — The local database used to store and retrieve historical waste data.

requirements.txt — Contains the necessary Python libraries to run the application.

Setup
Follow these steps to get EcoPulse running on your local machine:

Step 1: Clone the repository
Open your terminal and run the following command to download the project:

git clone https://github.com/Nelly444/EcoPulse

Step 2: Install dependencies

Navigate into the project folder and install the required Python packages:

pip install -r requirements.txt

Step 3: Run the application locally on your terminal

streamlit run user.py


