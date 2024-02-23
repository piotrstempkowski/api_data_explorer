import json

import requests
import matplotlib.pyplot as plt
from collections import defaultdict
from icecream import ic

from serializers import CompanyStockSerializer


def output_to_file(text):
    with open("output.txt", "a") as file:
        file.write(text + "\n")


ic.configureOutput(prefix="DEBUG: ", outputFunction=output_to_file)


class FinanceDataManager:
    def __init__(self, api_key):
        self.base_url = "https://financialmodelingprep.com/api"
        self.api_key = api_key

    def search_company(self, company_name):
        url = f"{self.base_url}/v3/search?query={company_name}&apikey={self.api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            raw_data = response.json()
            serializer = CompanyStockSerializer(data=raw_data, many=True)
            if serializer.is_valid():
                return serializer.validated_data
            else:
                ic(f"Błąd przy deserializacji danych: {serializer.errors}")
                return None
        except requests.RequestException as e:
            ic(f"Error when querying the API: {e}")
            return None

    def income_statement(self, symbol, years):
        url = f"{self.base_url}/v3/income-statement/{symbol}?limit={years}&apikey={self.api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            income_statement_raw_data = response.json()
            data = {}
            for record in income_statement_raw_data:
                year = record["calendarYear"]
                data[year] = {
                    "revenue": record["revenue"],
                    "gross_profit": record["grossProfit"],
                    "eps": record["eps"],
                    "ebitda": record["ebitda"]
                }
            return data
        except requests.RequestException as e:
            ic(f"Error when querying the API: {e}")
            return None

    def cash_flow_statement(self, symbol, years):
        url = f"{self.base_url}/v3/cash-flow-statement/{symbol}?limit={years}&apikey={self.api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            cash_flow_statement_raw_data = response.json()
            data = {}
            for record in cash_flow_statement_raw_data:
                year = record["calendarYear"]
                data[year] = {
                    "operating_cash_flow": record["operatingCashFlow"],
                    "capital_expenditure": record["capitalExpenditure"],
                    "free_cash_flow": record["freeCashFlow"]
                }
            return data
        except requests.RequestException as e:
            ic(f"Error when querying the API: {e}")
            return None

    def plot_income_statement(self, symbol, years):
        url = f"{self.base_url}/v3/income-statement/{symbol}?limit={years}&apikey={self.api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            income_statement = response.json()
            revenues = [income_statement[i]["revenue"] for i in range(len(income_statement))]
            reversed_revenues = list(reversed(revenues))
            profits = list(reversed([income_statement[i]["grossProfit"] for i in range(len(income_statement))]))
            plt.plot(reversed_revenues, label="Revenue")
            plt.plot(profits, label="Gross Profit")
            plt.legend(loc="upper right")
            return plt.show()
        except requests.RequestException as e:
            ic(f"Error when querying the API: {e}")
            return None

    def merge_financial_data(self, symbol, years):
        income_data = self.income_statement(symbol, years)
        cash_flow_data = self.cash_flow_statement(symbol, years)

        # usage of defaultdict in order to avoid KeyError and to have a default value for a key that does not exist

        combined_data = defaultdict(dict)

        for year, data in income_data.items():
            combined_data[year].update(data)

        for year, data in cash_flow_data.items():
            combined_data[year].update(data)

        return combined_data

    def create_csv(self, symbol, years):
        url = f"{self.base_url}/v3/income-statement/{symbol}?datatype=csv&limit={years}&apikey={self.api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(f"{symbol}_income_statement.csv", "wb") as file:
                file.write(response.content)
            return f"Created {symbol}_income_statement.csv"
        except requests.RequestException as e:
            ic(f"Error when querying the API: {e}")
            return None


if __name__ == "__main__":
    with open("api_key.json", "r") as file:
        api_key = json.load(file)["api_key"]

    fdm = FinanceDataManager(api_key)
    print(fdm.search_company("Tesla"))
    print(fdm.income_statement("TSLA", 5))
    print(fdm.plot_income_statement("TSLA", 30))
    print(fdm.create_csv("TSLA", 5))
    combined_data = fdm.merge_financial_data("TSLA", 5)
    print(combined_data)
