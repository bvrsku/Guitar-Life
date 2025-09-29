import subprocess
import sys
import os

# Запускаем тест
try:
    os.chdir(r"C:\REPOS\Guitar-Life")
    result = subprocess.run([sys.executable, "quick_test.py"], 
                          capture_output=True, text=True, timeout=10)
    
    print("=== STDOUT ===")
    print(result.stdout)
    
    if result.stderr:
        print("=== STDERR ===") 
        print(result.stderr)
        
    print(f"=== Return code: {result.returncode} ===")
    
except Exception as e:
    print(f"Ошибка запуска: {e}")