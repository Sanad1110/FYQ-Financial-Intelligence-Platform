#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "=================================="
echo "  FYQ v7.0 — تطبيق الويب"
echo "=================================="

if [ ! -d ".venv" ]; then
    echo "إنشاء البيئة الافتراضية..."
    python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt -q

echo ""
echo "جاري تشغيل التطبيق..."
echo "افتح المتصفح على: http://127.0.0.1:5050"
echo "للإيقاف اضغط Ctrl+C"
echo ""
python app.py
