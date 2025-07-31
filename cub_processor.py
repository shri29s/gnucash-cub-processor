import pdfplumber
import csv
import sys
import pandas as pd

from dotenv import load_dotenv
import groq
import os
import re

import yaml
import logging

from time import sleep

class Convert_pdf_csv:
    def __init__(self):
        # Initialize logging first
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("conversion.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logging.info("Starting PDF to CSV converter initialization")
        
        try:
            with open("config.yaml", "r") as file:
                config = yaml.safe_load(file)
            logging.info("Configuration file loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load config.yaml: {e}")
            raise

        try:
            load_dotenv(config["config"].get("env_file", ".env"))
            self.pdf_path = config["config"].get("pdf_path")
            self.csv_path = config["config"].get("csv_path")
            self.source_acc = config["config"].get("source_acc")
            logging.info(f"Configuration loaded - PDF: {self.pdf_path}, CSV: {self.csv_path}, Source Account: {self.source_acc}")
        except Exception as e:
            logging.error(f"Failed to load configuration parameters: {e}")
            raise

        try:
            self.client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
            logging.info("Groq API client initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Groq client: {e}")
            raise

        try:
            self.accounts = self.load_accounts(config["accounts"])
            logging.info(f"Account configuration loaded - {len(self.accounts['Expenses'])} expense accounts, {len(self.accounts['Income'])} income accounts")
        except Exception as e:
            logging.error(f"Failed to load account configuration: {e}")
            raise
            
        logging.info("PDF to CSV converter initialization completed successfully")

    def load_accounts(self, account_config):
        logging.info("Loading account configuration")
        expense_accounts = []
        income_accounts = []

        try:
            for expense in account_config['Expenses']:
                expense_accounts.append(expense["account"])

            for income in account_config["Income"]:
                income_accounts.append(income["account"])
            
            logging.info(f"Loaded {len(expense_accounts)} expense accounts and {len(income_accounts)} income accounts")
            return {"Expenses": expense_accounts, "Income": income_accounts}
        except Exception as e:
            logging.error(f"Error loading account configuration: {e}")
            raise

    def pdf_csv(self):
        logging.info(f"Starting PDF extraction from: {self.pdf_path}")
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf, open(self.csv_path, "w") as csv_file:
                writer = csv.writer(csv_file, lineterminator="\n")
                total_rows = 0
                
                logging.info(f"Processing {len(pdf.pages)} pages from PDF")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    logging.debug(f"Processing page {page_num}")
                    tables = page.extract_tables()
                    
                    for table_num, table in enumerate(tables, 1):
                        if table:
                            logging.debug(f"Processing table {table_num} on page {page_num} with {len(table)} rows")
                            for row in table:
                                writer.writerow(row)
                                total_rows += 1
                
                logging.info(f"PDF extraction completed successfully. Total rows extracted: {total_rows}")
        except Exception as e:
            logging.error(f"Error during PDF extraction: {e}")
            raise

    def mask_numbers(self, desc):
        return re.sub(r"\d", "x", desc)
    
    def categorize(self, desc: str):
        desc = str(desc).upper()
        desc = self.mask_numbers(desc)
        logging.debug(f"Categorizing transaction: '{desc}'")

        prompt = f'''
Classify the following bank transaction description into one of the following categories:
{self.accounts}
If unsure, return Expenses:Other or Income:Other.
Description: {desc}

NOTE:
If 'TO' in description, it is a debit.
If 'BY' in description, it is a credit.

* Please return only the category name.
'''
        message = {
            "role": "user",
            "content": prompt
        }

        try:
            response = self.client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[message],
                temperature=0.5,
                max_completion_tokens=50,
            )  

            category = response.choices[0].message.content.strip()
            category = category.split(" ")[-1]
            split = category.split(":")
            if len(split) <= 1 or (split[0] != "Expenses" and split[0] != "Income") or split[1] == "":
                if desc.startswith("TO"):
                    category = "Expenses:Other"
                else:
                    category = "Income:Other"
            logging.debug(f"Transaction '{desc}' categorized as: '{category}'")
            return category
        except Exception as e:
            logging.warning(f"Error categorizing transaction '{desc}': {e}. Using default category 'Expenses:Other'")
            return "Expenses:Other" 
        
    def currency_to_float(self, value):
        try:
            if isinstance(value, str):
                original_value = value
                value = value.replace('₹', '').replace('$', '')
                value = value.replace(',', '')
                logging.debug(f"Converting currency '{original_value}' to float: {float(value)}")
            return float(value)
        except Exception as e:
            logging.warning(f"Error converting currency value '{value}' to float: {e}. Returning 0.0")
            return 0.0
    
    def convert(self):
        logging.info("Starting conversion process")
        
        try:
            # Extract PDF to CSV
            self.pdf_csv()
            logging.info("PDF extraction completed, starting data processing")
            
            # Load and process the CSV data
            df = pd.read_csv(self.csv_path, header=None)
            initial_rows = len(df)
            logging.info(f"Loaded CSV with {initial_rows} rows")
            
            # Clean and process data
            df.drop_duplicates(inplace=True)
            after_dedup = len(df)
            logging.info(f"Removed {initial_rows - after_dedup} duplicate rows")
            
            df.drop(0, axis=0, inplace=True)
            df.drop([2, 5], axis=1, inplace=True)
            df.columns = ["Date", "Description", "Debit", "Credit"]
            logging.info("Data columns restructured and renamed")

            df['Account'] = [self.source_acc for i in df["Date"]]
            logging.info(f"Added source account '{self.source_acc}' to all transactions")
            
            # Filter out totals
            before_filter = len(df)
            df = df[df['Date'] != "TOTAL"]
            after_filter = len(df)
            logging.info(f"Filtered out {before_filter - after_filter} total rows")

            # Process monetary values
            df["Debit"] = df['Debit'].fillna(0)
            df["Credit"] = df['Credit'].fillna(0)

            df["Debit"] = df["Debit"].apply(self.currency_to_float)
            df["Credit"] = df["Credit"].apply(self.currency_to_float)
            df["Amount"] = df["Credit"] - df["Debit"]
            logging.info("Currency values processed and amounts calculated")

            # Categorize transactions
            logging.info("Starting transaction categorization using AI")
            df['Transfer Account'] = df.apply(lambda x: self.categorize(x["Description"]), axis=1)
            logging.info("Transaction categorization completed")

            # Final output
            df = df[["Date", "Description", "Account", "Transfer Account", "Amount"]]
            df.to_csv("statement.csv", index=False)
            
            final_rows = len(df)
            logging.info(f"Conversion completed successfully! Final output: {final_rows} transactions saved to statement.csv")
            
        except Exception as e:
            logging.error(f"Error during conversion process: {e}")
            raise

if __name__=="__main__":
    if not os.path.exists("config.yaml"):
        print("Config file not found!")
        sys.exit(1)

    try:
        conv = Convert_pdf_csv()
        conv.convert()
    except Exception as e:
        sys.exit(1)