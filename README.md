# 🏦 CUB Bank PDF to GnuCash CSV Converter

This Python project extracts transactions from **CUB (City Union Bank)** statement PDFs and converts them into a clean **CSV file** that can be imported into [GnuCash](https://www.gnucash.org/).

---

## 📁 Project Structure

```
STATEMENTS/
├── Notebooks/
│   └── cub_preprocess.ipynb    # Jupyter notebook for testing & exploration
├── venv/                       # Python virtual environment (excluded in .gitignore)
├── .gitignore                  # Git ignore rules
├── cub_processor.py            # Main script for PDF to CSV conversion
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── statement_pdf.pdf           # Example input PDF (CUB statement)
└── statement.csv               # Example output CSV for GnuCash import
```

---

## 📦 Installation

1. Clone the repo and navigate to the folder:

   ```bash
   git clone https://github.com/your-username/cub-gnucash-converter.git
   cd STATEMENTS
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Usage

Run the script using:

```bash
python cub_processor.py path/to/statement.pdf path/to/output.csv "SOURCE_ACCOUNT"
```

### Example:

```bash
python cub_processor.py statement_pdf.pdf statement.csv "CUB Savings"
```

- `statement_pdf.pdf`: Input CUB bank statement (text-based PDF).
- `statement.csv`: Output CSV file to be generated.
- `"CUB Savings"`: Source account name (used as metadata or in final CSV).

---

## 📅 Import into GnuCash

1. Open GnuCash.
2. Go to **File → Import → Import CSV**.
3. Select your `statement.csv`.
4. Map the columns appropriately:

   - Date
   - Description
   - Deposit
   - Withdrawal
   - Balance (optional)

5. Confirm and save!

---

## 🧪 Notebook (Optional)

You can use `Notebooks/cub_preprocess.ipynb` to explore, debug, or prototype the parsing logic interactively using `pdfplumber` or `pandas`.

---

## 📌 Notes

- The script assumes **text-based** PDFs. Scanned/image-based PDFs will not work unless OCR is added.
- `source_acc` is a string used for tracking the originating account (optional metadata).
- This is tailored for **CUB Bank**'s PDF structure. If your layout differs, you might need to adjust the parsing logic in `cub_processor.py`.

---

## 👯‍ License

MIT License – Free for personal and commercial use.
