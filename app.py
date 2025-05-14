import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data with caching for performance
@st.cache_data
def load_data():
    df_confirm = pd.read_csv("time_series_covid19_confirmed_global.csv")
    df_death = pd.read_csv("time_series_covid19_deaths_global.csv")
    df_recover = pd.read_csv("time_series_covid19_recovered_global.csv")
    df_confirm['Source'] = 'Confirmed'
    df_death['Source'] = 'Deaths'
    df_recover['Source'] = 'Recovered'
    combined_df = pd.concat([df_confirm, df_death, df_recover], ignore_index=True)
    combined_df['Province/State'] = combined_df['Province/State'].fillna(combined_df['Country/Region'])
    country_means = combined_df.groupby('Country/Region')[['Lat', 'Long']].mean()
    for idx, row in combined_df[combined_df['Lat'].isnull()].iterrows():
        country = row['Country/Region']
        if country in country_means.index:
            combined_df.at[idx, 'Lat'] = country_means.loc[country, 'Lat']
            combined_df.at[idx, 'Long'] = country_means.loc[country, 'Long']
    melted_df = combined_df.melt(
        id_vars=['Province/State', 'Country/Region', 'Lat', 'Long', 'Source'],
        var_name='Date',
        value_name='Cases'
    )
    melted_df['Date'] = pd.to_datetime(melted_df['Date'])
    return melted_df

st.title('COVID-19 Global Dashboard')

# Load and process data
melted_df = load_data()

# Sidebar for country selection
countries = melted_df['Country/Region'].unique()
selected_country = st.sidebar.selectbox('Select a country', countries)

# Filter and plot data
country_data = melted_df[(melted_df['Country/Region'] == selected_country) & (melted_df['Source'] == 'Confirmed')]

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(country_data['Date'], country_data['Cases'], marker='o')
ax.set_title(f'COVID-19 Confirmed Cases Over Time in {selected_country}')
ax.set_xlabel('Date')
ax.set_ylabel('Confirmed Cases')
ax.grid(True)
st.pyplot(fig)
