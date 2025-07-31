import pdfplumber
import csv
import sys
import pandas as pd

from dotenv import load_dotenv
import groq
import os
import re

import yaml

class Convert_pdf_csv:
    def __init__(self):
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)

        load_dotenv(config["config"].get("env_file", ".env"))
        self.pdf_path = config["config"].get("pdf_path")
        self.csv_path = config["config"].get("csv_path")
        self.source_acc = config["config"].get("source_acc")

        self.client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.accounts = self.load_accounts(config["accounts"])

    def load_accounts(self, account_config):
        expense_accounts = []
        income_accounts = []

        for expense in account_config['Expenses']:
            expense_accounts.append(expense["account"])

        for income in account_config["Income"]:
            income_accounts.append(income["account"])

        return {"Expenses": expense_accounts, "Income": income_accounts}

    def pdf_csv(self):
        with pdfplumber.open(self.pdf_path) as pdf, open(self.csv_path, "w") as csv_file:
            writer = csv.writer(csv_file, lineterminator="\n")
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        for row in table:
                            writer.writerow(row)

    def mask_numbers(self, desc):
        return re.sub(r"\d", "x", desc)

    def categorize(self, desc: str):
        desc = str(desc).upper()
        desc = self.mask_numbers(desc)

        prompt = f'''
Classify the following bank transaction description into one of the following categories:
{self.accounts}
If unsure, return Expenses:Other.
Description: {desc}
Return only the category name.
'''
        message = {
            "role": "user",
            "content": prompt
        }

        response = self.client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[message],
            temperature=0.5,
            max_completion_tokens=50,
        )  

        return response.choices[0].message.content.strip() 
        
    def currency_to_float(self, value):
        if isinstance(value, str):
            value = value.replace('₹', '').replace('$', '')
            value = value.replace(',', '')
        return float(value)
    
    def convert(self):
        self.pdf_csv()
        df = pd.read_csv(self.csv_path, header=None)
        df.drop_duplicates(inplace=True)
        df.drop(0, axis=0, inplace=True)
        df.drop([2, 5], axis=1, inplace=True)
        df.columns = ["Date", "Description", "Debit", "Credit"]

        df['Account'] = [self.source_acc for i in df["Date"]]
        df['Transfer Account'] = df.apply(lambda x: self.categorize(x["Description"]), axis=1)
        df = df[df['Date'] != "TOTAL"]

        df["Debit"] = df['Debit'].fillna(0)
        df["Credit"] = df['Credit'].fillna(0)

        df["Debit"] = df["Debit"].apply(self.currency_to_float)
        df["Credit"] = df["Credit"].apply(self.currency_to_float)
        df["Amount"] = df["Credit"] - df["Debit"]

        df = df[["Date", "Description", "Account", "Transfer Account", "Amount"]]
        df.to_csv("statement.csv", index=False)

if __name__=="__main__":
    if not os.path.exists("config.yaml"):
        print("Config file not found!")
        sys.exit(1)

    conv = Convert_pdf_csv()
    conv.convert()