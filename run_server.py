import os
import sys

# Добавление пути до папки app в sys.path, чтобы импорты в коде
# выглядили понятнее и красивее
sys.path.append(os.path.abspath(f"{os.curdir}/app"))

from app import app


if __name__ == "__main__":
    app.run(port=8080, host='127.0.0.1', use_reloader=True)
