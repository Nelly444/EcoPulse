# EcoPulse

EcoPulse is a waste management tracker designed to help small businesses reduce their environmental impact and save money. By tracking waste patterns, the app provides actionable insights that promote sustainable business practices and operational efficiency.

# Architecture
EcoPulse is built with a streamlined architecture where the primary interface and logic are integrated for efficiency.

- `user.py` — The core of the application. This Streamlit frontend handles all user input, data processing, and the main logic for tracking and visualization.
- `waste_log.csv` — Acts as the local database to store and retrieve waste entry history.
- `requirements.txt` — Lists the Python dependencies required to run the application locally.

# Setup

Step 1: Clone the repository
Open your terminal and run the following command to download the project:

```bash
git clone https://github.com/Nelly444/EcoPulse
```

Step 2: Install dependencies

Navigate into the project folder and install the required Python packages:
```bash
pip install -r requirements.txt
```

Step 3: Run the application locally on your terminal
```bash
streamlit run user.py
```

