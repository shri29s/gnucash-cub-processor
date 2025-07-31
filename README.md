# 🏦 CUB Bank PDF to GnuCash CSV Converter

This Python project extracts transactions from **CUB (City Union Bank)** statement PDFs and converts them into a clean **CSV file** that can be imported into [GnuCash](https://www.gnucash.org/). The application features **AI-powered transaction categorization** using Groq's LLaMA model and comprehensive logging for monitoring the conversion process.

---

## ✨ Features

- 📄 **PDF Extraction**: Extract transaction data from CUB bank statement PDFs
- 🤖 **AI Categorization**: Automatically categorize transactions using Groq's LLaMA 3 model
- ⚙️ **Configuration-Based**: Flexible YAML configuration for paths and account categories
- 📊 **Data Processing**: Clean and format transaction data for GnuCash import
- 📝 **Comprehensive Logging**: Detailed logs for monitoring and debugging
- 🔄 **Currency Handling**: Automatic conversion of currency values with error handling
- 🧹 **Data Cleaning**: Remove duplicates and filter out summary rows

---

## 📁 Project Structure

```
STATEMENTS/
├── Notebooks/
│   ├── cub_preprocess.ipynb    # Jupyter notebook for testing & exploration
│   └── statement.csv           # Sample processed data
├── venv/                       # Python virtual environment (excluded in .gitignore)
├── .env                        # Environment variables (GROQ_API_KEY)
├── .gitignore                  # Git ignore rules
├── config.yaml                 # Configuration file for paths and accounts
├── conversion.log              # Application logs
├── cub_processor.py            # Main script for PDF to CSV conversion
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── sample.py                   # Sample usage script
├── statement_pdf.pdf           # Example input PDF (CUB statement)
└── statement.csv               # Example output CSV for GnuCash import
```

---

## 📦 Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/shri29s/gnucash-cub-processor.git
   cd statements
   ```

2. **Create a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:

   Create a `.env` file in the project root:

   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

   Get your free Groq API key from [Groq Console](https://console.groq.com/).

5. **Configure the application**:

   Update `config.yaml` with your file paths and account preferences:

   ```yaml
   config:
     pdf_path: "statement_pdf.pdf"
     csv_path: "statement.csv"
     source_acc: "Assets:Bank Accounts:CUB"
     env_file: ".env"
   ```

---

## 🚀 Usage

The application uses configuration files, so you simply run:

```bash
python cub_processor.py
```

### Configuration

All settings are managed through `config.yaml`:

- **File Paths**: Input PDF and output CSV locations
- **Source Account**: GnuCash account name for the bank account
- **Account Categories**: Customizable expense and income categories for AI classification

### Example Output

The generated CSV file contains:

```csv
Date,Description,Account,Transfer Account,Amount
24/06/2025,TO ONL UPI/DR/xxxxxxxxxxxx/COFFEE T/YESB/PAYTMQR5ET/U::xxxxx,Assets:Bank Accounts:CUB,Expenses:Food,-22.0
23/06/2025,TO ONL UPI/DR/xxxxxxxxxxxx/UDEMY IN/HDFC/UDEMY ADYE/U::xxxxx,Assets:Bank Accounts:CUB,Expenses:Education,-479.0
24/06/2025,TO ONL UPI/DR/xxxxxxxxxxxx/D R R PH/ICIC/DRRPHARMAC/U::xxxxx,Assets:Bank Accounts:CUB,Expenses:Medical,-539.0
```

---

## 🤖 AI-Powered Categorization

The application automatically categorizes transactions using Groq's LLaMA 3 model. Categories include:

### Expense Categories:

- Food, Groceries, Rent, Utilities
- Transportation, Fuel, Shopping
- Medical, Subscriptions, Education
- Entertainment, Travel, Fees/Charges
- Other (fallback category)

### Income Categories:

- Salary, UPI Transfer, IMPS Transfer
- Refund/Reimbursement, Interest/Dividend
- Family, Other

Categories are fully customizable in `config.yaml`.

---

## � Import into GnuCash

1. Open GnuCash
2. Go to **File → Import → Import Transactions from CSV**
3. Select your generated `statement.csv`
4. Map the columns:
   - **Date**: Date column
   - **Description**: Description column
   - **Account**: Account column
   - **Transfer Account**: Transfer Account column
   - **Amount**: Amount column (positive for credits, negative for debits)
5. Review and import the transactions

---

## 📝 Logging

The application provides comprehensive logging:

- **Console Output**: Real-time progress updates
- **Log File**: Detailed logs saved to `conversion.log`
- **Log Levels**: INFO, DEBUG, WARNING, and ERROR messages
- **Monitoring**: Track PDF extraction, AI categorization, and data processing

Example log output:

```
2025-07-31 10:30:15 - INFO - Starting PDF to CSV converter initialization
2025-07-31 10:30:16 - INFO - Configuration loaded - PDF: statement_pdf.pdf, CSV: statement.csv
2025-07-31 10:30:16 - INFO - Groq API client initialized successfully
2025-07-31 10:30:17 - INFO - Starting PDF extraction from: statement_pdf.pdf
2025-07-31 10:30:18 - INFO - Starting transaction categorization using AI
2025-07-31 10:30:25 - INFO - Conversion completed successfully! Final output: 65 transactions
```

---

## 🧪 Development & Testing

Use the Jupyter notebook for development and testing:

```bash
jupyter notebook Notebooks/cub_preprocess.ipynb
```

The notebook allows you to:

- Explore PDF structure interactively
- Test parsing logic
- Debug categorization results
- Prototype new features

---

## � Requirements

- Python 3.7+
- Groq API key (free tier available)
- Text-based PDF statements from CUB Bank

### Dependencies:

- `pdfplumber`: PDF text extraction
- `pandas`: Data processing and manipulation
- `groq`: AI-powered transaction categorization
- `python-dotenv`: Environment variable management
- `pyyaml`: Configuration file parsing

---

## ⚠️ Important Notes

- **PDF Format**: The script works with **text-based** PDFs only. Scanned/image-based PDFs require OCR preprocessing.
- **Bank-Specific**: Tailored for **CUB Bank**'s statement format. Other banks may require modifications.
- **API Usage**: Uses Groq's free tier for AI categorization. Monitor your API usage limits.
- **Data Privacy**: Transaction data is sent to Groq for categorization (descriptions are masked with numbers replaced by 'x').
- **Accuracy**: AI categorization achieves ~85-90% accuracy. Review and adjust categories as needed.

---

## 🚨 Troubleshooting

### Common Issues:

1. **"Config file not found"**

   - Ensure `config.yaml` exists in the project directory

2. **"Failed to initialize Groq client"**

   - Check your `GROQ_API_KEY` in the `.env` file
   - Verify API key is valid and has remaining credits

3. **"PDF extraction failed"**

   - Ensure PDF is text-based (not scanned)
   - Check if PDF file path is correct in `config.yaml`

4. **Poor categorization results**
   - Review and customize account categories in `config.yaml`
   - Check transaction descriptions in logs for debugging

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## � License

MIT License – Free for personal and commercial use.

---

## 🙏 Acknowledgments

- [pdfplumber](https://github.com/jsvine/pdfplumber) for PDF processing
- [Groq](https://groq.com/) for fast AI inference
- [GnuCash](https://www.gnucash.org/) for personal finance management
