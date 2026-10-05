@echo off
chcp 65001 >nul
echo ============================================
echo   Generador de recibos PDF por universidad
echo   Lee la pestana 'datos' del Google Sheet,
echo   agrupa por univ/alumno, incrusta el logo
echo   y exporta: pdfs\Universidad - Nombre Apellido.pdf
echo ============================================
"C:\venv\Scripts\python.exe" "%~dp0generar_recibos.py" %*
echo.
echo Listo. PDFs en: %~dp0pdfs
pause
