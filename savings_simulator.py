import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objs as go

# Define translations
translations = {
    'en': {
        'title': 'Savings Simulator',
        'sidebar_title': 'Simulation Parameters',
        'initial_amount': 'Initial Amount (€)',
        'monthly_contribution': 'Monthly Contribution (€)',
        'interest_rate': 'Annual Interest Rate (%)',
        'duration': 'Duration (years)',
        'entry_fees': 'Entry Fees (%)',
        'management_fees': 'Annual Management Fees (%)',
        'future_value': 'Future Value of Savings after {years} Years',
        'balance_title': 'Savings Balance Evolution Over Years',
        'capital_vs_interests': 'Savings Distribution: Capital vs Interests<br>Total: {total}',
        'fees_distribution': 'Fees Distribution<br>Total: {total}',
        'total_no_fees': 'Total (No Fees)',
        'capital': 'Capital',
        'interests': 'Interests',
        'summary': 'Summary',
        'total_contributions': 'Total Contributions',
        'total_fees': 'Total Fees Paid',
        'net_gains': 'Net Gains After Fees',
        'future_value_summary': 'The future value of your savings after {years} years is estimated to be {future_value}, including total contributions of {total_contributions}, and total fees paid amounting to {total_fees}. Your net gains, after subtracting the fees, are {net_gains}.'
    },
    'fr': {
        'title': 'Simulateur d\'Épargne',
        'sidebar_title': 'Paramètres de Simulation',
        'initial_amount': 'Montant Initial (€)',
        'monthly_contribution': 'Versement Mensuel (€)',
        'interest_rate': 'Taux d\'Intérêt Annuel (%)',
        'duration': 'Durée (années)',
        'entry_fees': 'Frais d\'Entrée (%)',
        'management_fees': 'Frais de Gestion Annuel (%)',
        'future_value': 'Valeur Future de l\'Épargne après {years} années',
        'balance_title': 'Évolution du Solde de l\'Épargne au Fil des Années',
        'capital_vs_interests': 'Répartition Épargne: Capital vs Intérêts<br>Total: {total}',
        'fees_distribution': 'Répartition des Frais<br>Total: {total}',
        'total_no_fees': 'Total (sans frais)',
        'capital': 'Capital',
        'interests': 'Intérêts',
        'summary': 'Résumé',
        'total_contributions': 'Contributions Totales',
        'total_fees': 'Frais Totaux Payés',
        'net_gains': 'Gains Nets Après Frais',
        'future_value_summary': 'La valeur future de votre épargne après {years} années est estimée à {future_value}, y compris des contributions totales de {total_contributions}, et des frais totaux payés de {total_fees}. Vos gains nets, après déduction des frais, sont de {net_gains}.'
    }
}

def get_translations(lang):
    return translations.get(lang, translations['en'])

def calculate_future_value(principal, monthly_contribution, rate, years, entry_fees_percentage, management_fees_percentage):
    months = years * 12
    monthly_rate = rate / 12 / 100
    initial_amount = principal
    future_value_no_fees = principal * (1 + monthly_rate)**months

    capital_values = [principal]
    total_values_no_fees = [future_value_no_fees]
    future_values = [future_value_no_fees]

    for month in range(1, months + 1):
        future_value_no_fees += monthly_contribution * (1 + monthly_rate)**(months - month)
        future_value = future_value_no_fees
        capital = principal + monthly_contribution * month
        future_values.append(future_value)
        capital_values.append(capital)
        total_values_no_fees.append(future_value_no_fees)

    entry_fees = initial_amount * (entry_fees_percentage / 100)
    future_value -= entry_fees

    if management_fees_percentage > 0:
        management_fees = future_value * (management_fees_percentage / 100)
        future_value -= management_fees
    else:
        management_fees = 0

    capital = principal + monthly_contribution * months
    interests = future_value - capital

    future_value = max(future_value, 0)
    interests = max(interests, 0)
    future_values = np.nan_to_num(future_values)
    capital_values = np.nan_to_num(capital_values)

    interests_values = [fv - cv for fv, cv in zip(future_values, capital_values)]

    return future_value, future_values, capital_values, total_values_no_fees, interests, entry_fees, management_fees, interests_values

def prepare_data_for_area_chart(total_values_no_fees, capital_values, interests_values, years):
    df = pd.DataFrame({
        'Year': np.arange(0, years + 1),
        'Total (No Fees)': [total_values_no_fees[i * 12] if i * 12 < len(total_values_no_fees) else total_values_no_fees[-1] for i in range(years + 1)],
        'Capital': [capital_values[i * 12] if i * 12 < len(capital_values) else capital_values[-1] for i in range(years + 1)],
        'Interests': [interests_values[i * 12] if i * 12 < len(interests_values) else interests_values[-1] for i in range(years + 1)]
    })
    return df

def plot_area_chart(df, colors, currency_symbol):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Total (No Fees)'], fill='tozeroy', name='Total (No Fees)', line=dict(color=colors['total_no_fees'], width=2)))
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Capital'], fill='tozeroy', name='Capital', line=dict(color=colors['capital'], width=2)))
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Interests'], fill='tozeroy', name='Interests', line=dict(color=colors['interests'], width=2)))
    
    fig.update_layout(
        title=translations[lang]['balance_title'],
        xaxis_title='Year',
        yaxis_title=f'Balance ({currency_symbol})',
        xaxis=dict(
            tickmode='linear',
            dtick=1,
            tickvals=df['Year'].tolist(),
            ticktext=[str(int(year)) for year in df['Year'].tolist()]
        ),
        yaxis=dict(
            title=f'Balance ({currency_symbol})',
            gridcolor='rgba(0,0,0,0.1)'
        ),
        margin=dict(l=0, r=0, t=80, b=0),
        legend=dict(
            x=0, 
            y=1.1, 
            orientation='h',
            bordercolor='rgba(0,0,0,0.1)'
        ),
        hovermode='closest'
    )
    
    return fig

def plot_pie_chart(labels, sizes, title, currency_symbol, height=400):
    fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=0.3, textinfo='label+percent', hoverinfo='label+value')])
    fig.update_layout(
        title=title,
        showlegend=True,
        height=height,  # Set the height for the pie chart
        margin=dict(l=0, r=0, t=80, b=0)
    )
    return fig

# Streamlit app
st.set_page_config(page_title=translations['en']['title'], layout='wide')

# Language selection
lang = st.sidebar.selectbox('Select Language', options=['en', 'fr'])

# Get translations based on selected language
trans = get_translations(lang)

st.title(trans['title'])

# Currency selection
currency_options = {
    '$': 'US Dollar',
    '€': 'Euro',
    '¥': 'Japanese Yen',
    '£': 'British Pound Sterling',
    'AU$': 'Australian Dollar',
    'C$': 'Canadian Dollar',
    'CHF': 'Swiss Franc',
    '¥': 'Chinese Yuan',
    'kr': 'Swedish Krona',
    'NZ$': 'New Zealand Dollar'
}
currency_symbol = st.sidebar.selectbox('Select Currency', options=list(currency_options.keys()))

# Sidebar with input fields and sliders
st.sidebar.header(trans['sidebar_title'])

# Principal
principal = st.sidebar.slider('Initial Amount', min_value=0, max_value=1000000, value=100000, step=1000)
custom_principal = st.sidebar.number_input('Or enter amount manually:', min_value=0, max_value=1000000, value=principal, step=1000)
principal = custom_principal if custom_principal != principal else principal

# Monthly Contribution
monthly_contribution = st.sidebar.slider(trans['monthly_contribution'], min_value=0, max_value=10000, value=100, step=50)

# Interest Rate
rate = st.sidebar.slider(trans['interest_rate'], min_value=0.0, max_value=20.0, value=3.0, step=0.1)

# Years
years = st.sidebar.slider(trans['duration'], min_value=1, max_value=50, value=10)

# Entry Fees
entry_fees_percentage = st.sidebar.slider(trans['entry_fees'], min_value=0.0, max_value=10.0, value=1.0, step=0.1)

# Management Fees
management_fees_percentage = st.sidebar.slider(trans['management_fees'], min_value=0.0, max_value=10.0, value=1.0, step=0.1)

# Calculate and display results
future_value, future_values, capital_values, total_values_no_fees, interests, entry_fees, management_fees, interests_values = calculate_future_value(
    principal, monthly_contribution, rate, years, entry_fees_percentage, management_fees_percentage)

st.subheader(trans['future_value'].format(years=years))
st.write(f"{currency_symbol}{future_value:,.2f}")

# Prepare data for charts
df = prepare_data_for_area_chart(total_values_no_fees, capital_values, interests_values, years)

# Colors
colors = {
    'total_no_fees': '#B2B0EA',
    'capital': '#BDE2B9',
    'interests': '#73C5C5'
}

# Plotting charts
fig_balance = plot_area_chart(df, colors, currency_symbol)

# Pie charts
fees_distribution_labels = [trans['entry_fees'], trans['management_fees']]
fees_distribution_sizes = [entry_fees, management_fees]
fees_distribution_title = trans['fees_distribution'].format(total=f"{currency_symbol}{entry_fees + management_fees:,.2f}")

fig_fees_distribution = plot_pie_chart(
    fees_distribution_labels,
    fees_distribution_sizes,
    fees_distribution_title,
    currency_symbol,
    height=400
)

capital_vs_interests_labels = [trans['capital'], trans['interests']]
capital_vs_interests_sizes = [capital_values[-1], interests]
capital_vs_interests_title = trans['capital_vs_interests'].format(total=f"{currency_symbol}{capital_values[-1] + interests:,.2f}")

fig_capital_vs_interests = plot_pie_chart(
    capital_vs_interests_labels,
    capital_vs_interests_sizes,
    capital_vs_interests_title,
    currency_symbol,
    height=400
)

# Plotting charts
st.plotly_chart(fig_balance)

col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_capital_vs_interests)

with col2:
    st.plotly_chart(fig_fees_distribution)

st.markdown("""
    <div style="text-align: center; padding-top: 100px;">
        <a href="https://github.com/czantoine/Savings-Simulator" target="_blank">
            <img src="https://img.shields.io/github/stars/czantoine/Savings-Simulator?style=social" alt="Star on GitHub">
        </a>
    </div>
    <div style="text-align: center; padding-top: 20px;">
        <a href="https://www.linkedin.com/in/antoine-cichowicz-837575b1/" target="_blank" style="margin: 0; padding: 0; display: inline-block;">
            <i class="fab fa-linkedin" style="font-size: 30px; margin: 0 10px; color: #A9A9A9; vertical-align: middle;"></i>
        </a>
        <a href="https://twitter.com/cz_antoine" target="_blank" style="margin: 0; padding: 0; display: inline-block;">
            <i class="fab fa-twitter" style="font-size: 30px; margin: 0 10px; color: #A9A9A9; vertical-align: middle;"></i>
        </a>
        <a href="https://github.com/czantoine" target="_blank" style="margin: 0; padding: 0; display: inline-block;">
            <i class="fab fa-github" style="font-size: 30px; margin: 0 10px; color: #A9A9A9; vertical-align: middle;"></i>
        </a>
    </div>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
""", unsafe_allow_html=True)