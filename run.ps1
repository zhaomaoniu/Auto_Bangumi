# ����������⻷�������� main.py
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    Set-Location backend/src;
    .\..\..\venv\Scripts\Activate.ps1;
    python main.py;
"

# ����ǰ�˿���������
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    Set-Location webui;
    npm run dev;
"
