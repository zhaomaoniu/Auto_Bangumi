# 启动后端虚拟环境并运行 main.py
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    Set-Location backend/src;
    .\..\..\venv\Scripts\Activate.ps1;
    python main.py;
"

# 启动前端开发服务器
Start-Process powershell -ArgumentList "-NoExit", "-Command", "
    Set-Location webui;
    npm run dev;
"
