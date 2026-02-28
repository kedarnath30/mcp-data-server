@echo off
echo Installing DashAI V6 Enhanced Dependencies...
echo.

pip install streamlit>=1.28.0
pip install pandas>=2.0.0
pip install plotly>=5.17.0
pip install anthropic>=0.7.0
pip install python-dotenv>=1.0.0
pip install numpy>=1.24.0
pip install reportlab>=4.0.0
pip install python-pptx>=0.6.21
pip install openpyxl>=3.1.0

echo.
echo Installation complete!
echo.
echo To run DashAI V6:
echo streamlit run dashboard_ai_enhanced.py
echo.
pause
