# yahoo-finance-ticker-analysis
Takes security parameters and outputs growth analysis for key financial metrics

# Dependencies
  - Java 16 or higher
  - Python3.8 or higher
  - Have Google Chrome installed 

# Create Excel file (example using AAPL, MSFT, TSLA)
``` python3 create_excel.py -t AAPL,MSFT,TSLA ``` 

# Analyze the excel file for Annual year
``` java -jar AnnualAndFuture.jar ```

# Analyze the excel file for Quarterly year
``` java -jar Quarterly.jar ```
