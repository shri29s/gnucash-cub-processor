import pdfplumber
import csv
import sys
import pandas as pd

class Convert_pdf_csv:
    def __init__(self, pdf_path, csv_path, source_acc):
        self.pdf_path = pdf_path
        self.csv_path = csv_path
        self.source_acc = source_acc

    def pdf_csv(self):
        with pdfplumber.open(self.pdf_path) as pdf, open(self.csv_path, "w") as csv_file:
            writer = csv.writer(csv_file, lineterminator="\n")
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        for row in table:
                            writer.writerow(row)

    def categorize(self, desc: str):
        desc = str(desc).upper()
        result = ""
        if "TO" in desc:
            result += "Expenses:"
        else:
            result += "Income:"

        if "UPI" in desc:
            result += "UPI"
        elif "INTEREST" in desc:
            result += "Interest"
        elif "IMPS" in desc:
            result += "IMPS"
        else:
            result += "Misc"
        
        return result
        
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
    pdf_path = sys.argv[1]
    csv_path = sys.argv[2]
    source_acc = sys.argv[3]

    conv = Convert_pdf_csv(pdf_path, csv_path, source_acc)
    conv.convert()