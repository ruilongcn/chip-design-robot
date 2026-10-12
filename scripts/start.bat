@echo off
rem 芯片设计智能体团队 - 一键启动
cd /d "%~dp0.."
where python >nul 2>nul || (echo [ERROR] 未找到 Python，请先安装 Python 3.11+ & pause & exit /b 1)
python scripts\start_backend.py
pause
