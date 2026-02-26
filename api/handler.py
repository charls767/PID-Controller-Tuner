from streamlit.web import cli as stcli
import sys
import os

def handler(request):
    sys.argv = ["streamlit", "run", "app/main.py", "--server.port=3000", 
                "--server.headless=true", "--logger.level=error"]
    stcli.main()
    return {"statusCode": 200}
