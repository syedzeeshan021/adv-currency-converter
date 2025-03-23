import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from io import BytesIO
import altair as alt

# Set page configuration as the very first command
st.set_page_config(page_title="Advanced Currency Converter", layout="wide")

# --- Define API KEY for real-time data (Exchangerate-API) ---
API_KEY = "cbee27828ca6903f8d148ae4"  # Replace with your actual API key if needed

# --- Sidebar Theme Toggle ---
theme_choice = st.sidebar.radio("Choose Theme", options=["Dark 🌙", "Light ☀️"], index=0)

if theme_choice == "Dark 🌙":
    custom_css = """
    <style>
    body { background-color: #000000; color: white; }
    .stApp { background-color: #000000; color: white; }
    .st-eb { background-color: #333333; color: white; }
    .st-bb { background-color: #444444; color: white; }
    .st-d3 { background-color: #555555; color: white; }
    div.st-bf { color: white; }
    .link-button {
        display: inline-block; padding: 10px 20px; margin: 10px 0; font-size: 16px;
        background-color: #555555; color: white; text-decoration: none; border-radius: 5px;
        transition: background-color 0.3s;
    }
    .link-button:hover { background-color: #777777; }
    </style>
    """
else:
    custom_css = """
    <style>
    body { background-color: #f0f0f0; color: #333333; }
    .stApp { background-color: #f0f0f0; color: #333333; }
    .st-eb { background-color: #ffffff; color: #333333; }
    .st-bb { background-color: #e0e0e0; color: #333333; }
    .st-d3 { background-color: #d0d0d0; color: #333333; }
    div.st-bf { color: #333333; }
    .link-button {
        display: inline-block; padding: 10px 20px; margin: 10px 0; font-size: 16px;
        background-color: #e0e0e0; color: #333333; text-decoration: none; border-radius: 5px;
        transition: background-color 0.3s;
    }
    .link-button:hover { background-color: #c0c0c0; }
    </style>
    """
st.markdown(custom_css, unsafe_allow_html=True)

# --- Title and Description ---
st.title("Advanced Currency Converter 💱")
st.write("Convert currencies with real-time and historical exchange rates. Enjoy the experience! 😊")

# --- Currency Data Functions ---
@st.cache_data(ttl=3600)
def get_currency_symbols(api_key=None):
    """Fetches currency symbols from the API or returns a hard-coded list."""
    if api_key:
        base_url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
        try:
            response = requests.get(base_url)
            response.raise_for_status()
            data = response.json()
            return list(data.get("conversion_rates", {}).keys())
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error fetching currency symbols: {e}")
            return []
    else:
        return ['USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF', 'CNY', 'SEK', 'NZD',
                'MXN', 'SGD', 'HKD', 'NOK', 'KRW', 'TRY', 'RUB', 'INR', 'BRL', 'ZAR',
                'AED', 'SAR']

@st.cache_data(ttl=3600)
def get_exchange_rate(from_currency, to_currency, api_key=None):
    """Fetches the real-time exchange rate using the Exchangerate-API."""
    if api_key:
        base_url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{from_currency}"
        try:
            response = requests.get(base_url)
            response.raise_for_status()
            data = response.json()
            return data.get("conversion_rates", {}).get(to_currency)
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Error fetching real-time rate: {e}")
            return None
    else:
        # Fallback hard-coded rates
        hardcoded_rates = {
            ("USD", "EUR"): 0.92, ("EUR", "USD"): 1.09,
            ("USD", "JPY"): 149.57, ("JPY", "USD"): 0.0067,
            ("GBP", "USD"): 1.27, ("USD", "GBP"): 0.79,
            ("USD", "AUD"): 1.52, ("AUD", "USD"): 0.66,
            ("USD", "CAD"): 1.36, ("CAD", "USD"): 0.73,
        }
        if (from_currency, to_currency) in hardcoded_rates:
            return hardcoded_rates[(from_currency, to_currency)]
        st.error(f"❌ No API key provided and no hard-coded data for {from_currency} to {to_currency}.")
        return None

# --- NBP API Functions for Historical Data ---
def get_nbp_rate_adjusted(currency: str, date: str):
    """
    Fetches the NBP mid rate for a given currency on a specific date.
    If no data is available (e.g., due to weekends or holidays), it will try previous dates.
    For PLN, returns 1.0.
    The fallback period is increased to 30 days.
    """
    if currency.upper() == "PLN":
        return 1.0
    current_date = datetime.strptime(date, "%Y-%m-%d")
    fallback_days = 0
    max_fallback = 30  # Increased fallback limit
    while fallback_days < max_fallback:
        url = f"http://api.nbp.pl/api/exchangerates/rates/A/{currency}/{current_date.strftime('%Y-%m-%d')}/?format=json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            rate = data["rates"][0]["mid"]
            return rate
        except requests.exceptions.HTTPError:
            current_date -= timedelta(days=1)
            fallback_days += 1
    st.error(f"❌ Could not find data for {currency} within the last {max_fallback} days.")
    return None

@st.cache_data
def get_historical_rate_nbp(from_currency, to_currency, date_str):
    """
    Calculates the conversion rate on a given date using NBP data,
    adjusting for weekends/holidays by checking previous dates if necessary.
    """
    rate_from = get_nbp_rate_adjusted(from_currency, date_str)
    rate_to = get_nbp_rate_adjusted(to_currency, date_str)
    if rate_from is None or rate_to is None:
        return None
    if from_currency.upper() == "PLN":
        return 1 / rate_to
    elif to_currency.upper() == "PLN":
        return rate_from
    else:
        return rate_from / rate_to

@st.cache_data
def get_historical_rates_for_chart_nbp(from_currency, to_currency, start_date, end_date):
    """
    Fetches historical exchange rates from NBP for each day in the specified range.
    Note: NBP does not publish rates on weekends/holidays.
    """
    historical_data = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        rate = get_historical_rate_nbp(from_currency, to_currency, date_str)
        if rate is not None:
            historical_data.append({"Date": current_date, "Rate": rate})
        current_date += timedelta(days=1)
    return historical_data

# --- Main Layout ---
col1, col2, col3 = st.columns(3)

with col1:
    amount = st.number_input("Enter Amount 💵", min_value=0.01, value=1.00, step=0.01)
    if amount < 0.01:
        st.warning("⚠️ Amount must be greater than 0.01")

with col2:
    all_currencies = get_currency_symbols(API_KEY)
    from_currency = st.selectbox("From Currency 🌍", all_currencies, index=all_currencies.index('USD') if 'USD' in all_currencies else 0)

with col3:
    to_currency = st.selectbox("To Currency 🌏", all_currencies, index=all_currencies.index('EUR') if 'EUR' in all_currencies else 1)

# --- Real-Time Conversion ---
if st.button("Convert 🔄"):
    rate = get_exchange_rate(from_currency, to_currency, API_KEY)
    if rate is not None:
        converted_amount = amount * rate
        st.success(f"✅ {amount} {from_currency} = {converted_amount:.2f} {to_currency}")
    else:
        st.error(f"❌ Error converting from {from_currency} to {to_currency}")

# --- Historical Rates Section ---
st.subheader("Historical Exchange Rates 📅")
col4, col5 = st.columns(2)
with col4:
    history_date = st.date_input("Select Date", value=datetime.today())
    if history_date > datetime.today().date():
        st.error(f"❌ Cannot check data in the future. Date must be before {datetime.today().strftime('%Y-%m-%d')}")
with col5:
    start_date_chart = st.date_input("Start Date for Chart 📈", value=datetime.today() - timedelta(days=30))
    end_date_chart = st.date_input("End Date for Chart 📊", value=datetime.today())
    if end_date_chart > datetime.today().date():
        st.error("❌ End date for the chart cannot be in the future.")

if start_date_chart >= end_date_chart:
    st.error("❌ Start date must be before end date.")

if st.button("Get Historical Rate 📅"):
    date_str = history_date.strftime("%Y-%m-%d")
    historical_rate = get_historical_rate_nbp(from_currency, to_currency, date_str)
    if historical_rate is not None:
        st.write(f"On {date_str}, 1 {from_currency} was equal to {historical_rate:.4f} {to_currency} (NBP data) ✅")
    else:
        st.write(f"❌ Could not fetch historical rate for {from_currency} to {to_currency} on {date_str}")

# --- Download Current Rates ---
st.subheader("Download Exchange Rate Data ⬇️")
download_data = None
if st.button("Download Current Rates ⬇️"):
    rates = {}
    for currency in all_currencies:
        rate = get_exchange_rate("USD", currency, API_KEY)
        if rate is not None:
            rates[currency] = rate
    if not rates:
        st.error("❌ Could not download the data for the exchange rates.")
    else:
        df = pd.DataFrame(list(rates.items()), columns=["Currency", "Rate (USD)"])
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Exchange Rates", index=False)
        buffer.seek(0)
        download_data = buffer.getvalue()

if download_data:
    st.download_button(
        label="Download Exchange Rates ⬇️",
        data=download_data,
        file_name="exchange_rates.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# --- Historical Trend Chart using Altair ---
st.subheader("Historical Rate Trend 📈")
if st.button("Show Trend Chart 📊"):
    chart_end_date = end_date_chart if end_date_chart <= datetime.today().date() else datetime.today().date()
    historical_rates_data = get_historical_rates_for_chart_nbp(from_currency, to_currency, start_date_chart, chart_end_date)
    if historical_rates_data and len(historical_rates_data) > 0:
        df_chart = pd.DataFrame(historical_rates_data)
        # Build an Altair chart
        chart = alt.Chart(df_chart).mark_line(point=True).encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Rate:Q", title="Exchange Rate"),
            tooltip=["Date:T", "Rate:Q"]
        ).properties(
            title=f"{from_currency} to {to_currency} Exchange Rate Trend (NBP)",
            width=700,
            height=400
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("⚠️ No historical data available for the selected date range. Please choose a different range.")

# --- Link to NBP Current Rate List ---
st.markdown("### Check Out the Latest Exchange Rates 🌐")
st.markdown(
    '<a href="https://www.nbp.com.pk/ratesheet/index.aspx" target="_blank" class="link-button">View Current Rate List</a>',
    unsafe_allow_html=True,
)

# --- Footer ---
st.markdown("---")
