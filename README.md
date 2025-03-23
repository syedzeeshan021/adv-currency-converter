# Advanced Currency Converter
Advanced Currency Converter is a dynamic, interactive Streamlit-based web application that provides both real-time and historical exchange rate data. It integrates data from Exchangerate-API for live rates and the NBP API for historical rates. The app offers an engaging user interface with dark/light theme toggling, interactive trend charts, and emojis for a fun, user-friendly experience.

# Features

# Real-Time Conversion: 
Convert currencies instantly using live data from Exchangerate-API.

# Historical Data:
Retrieve historical exchange rates from the National Bank of Poland (NBP) API, with automatic fallback for weekends and holidays.
# Interactive Trend Charts:

Visualize historical exchange rate trends with interactive Plotly charts.
# Download Data:

Export current exchange rate data as an Excel file for offline use.
# Theme Toggle:

Switch seamlessly between dark 🌙 and light ☀️ modes to suit your preference.
# User-Friendly Interface:

Enjoy a dynamic experience with an intuitive layout and engaging emojis throughout the UI.
# Installation

Clone the repository:
git clone https://github.com/yourusername/advanced-currency-converter.git cd advanced-currency-converter
Create and activate a virtual environment (optional but recommended):
python -m venv venv source venv/bin/activate # On Windows use: venv\Scripts\activate

# Install the required packages:
pip install -r requirements.txt Make sure your requirements.txt includes the following libraries:
streamlit
pandas
requests
plotly
xlsxwriter

# Usage
Run the Streamlit app: streamlit run your_script_name.py
# Interact with the application:
Use the sidebar to toggle between Dark 🌙 and Light ☀️ themes.
Enter the amount you wish to convert, select the source and target currencies, then click Convert 🔄 for real-time conversion.
Select a historical date to view past exchange rates and generate a trend chart.
Download the latest exchange rates as an Excel file using the Download Exchange Rates ⬇️ button.
Click the provided link button to view the current rate list on the NBP website.

## Configuration
# API Key:
The application uses an API key for Exchangerate-API to fetch real-time exchange rates. Replace the placeholder API_KEY in the code with your actual API key if needed.

# NBP Data Integration:
Historical exchange rate data is retrieved from the NBP API. The app includes a fallback mechanism to account for weekends and holidays when data might not be available.

# Contributing
Contributions are welcome! Feel free to fork this repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

# License
This project is licensed under the MIT License. See the LICENSE file for details.

# Acknowledgments
Exchange rate-API for providing real-time exchange rate data.
NBP API for historical exchange rate data.
The Streamlit and Plotly communities for their amazing open-source tools that made this project possible.

