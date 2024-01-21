from flask import Flask, render_template, redirect, url_for, request, Response
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import plotly
import plotly.express as px
import json
import requests
import pandas as pd
import os

API_KEY = os.environ.get("STOCK_KEY")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
Bootstrap(app)


class CompanyForm(FlaskForm):
    company = StringField(label='Enter Company Name to check stock details:', validators=[DataRequired()])
    submit = SubmitField(label='Submit')


@app.route("/", methods=['GET', 'POST'])
def home():
    form = CompanyForm()
    if form.validate_on_submit():
        company = form.company.data
        final_url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={company}&apikey={API_KEY}"
        response_1 = requests.get(url=final_url)
        search_result = response_1.json()["bestMatches"]
        return render_template("select.html", companies=search_result)
    return render_template("index.html", form=form)


@app.route("/get_stock", methods=['GET'])
def get_stock():
    company_symbol = request.args.get('company_id')
    final_url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={company_symbol}&apikey={API_KEY}"
    response_1 = requests.get(url=final_url)
    searched_company = response_1.json()["bestMatches"][0]
    response = requests.get(url=f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={company_symbol}&apikey={API_KEY}")
    data = response.json()["Time Series (Daily)"]
    df_prices = pd.DataFrame.from_dict(data)
    df_days = pd.DataFrame.transpose(df_prices)
    response_2 = requests.get(
        url=f"https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={company_symbol}&apikey={API_KEY}")
    data_2 = response_2.json()["Monthly Time Series"]
    df_prices_2 = pd.DataFrame.from_dict(data_2)
    df_months = pd.DataFrame.transpose(df_prices_2)
    df_months['4. close'] = pd.to_numeric(df_months['4. close'])
    fig = px.line(x=df_months.index[:24],
                  y=df_months['4. close'][:24],
                  title=f"{company_symbol} Monthly stock price trend",
                  labels={'y': 'Price', 'x': 'Month'},
                  markers=True)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('stock.html', df_days=df_days, graphJSON=graphJSON, company=searched_company)


if __name__ == '__main__':
    app.run(debug=True)