#!/bin/bash
# Diagnostic script to identify homework upload issues

echo "🔍 HOMEWORK UPLOAD DIAGNOSTICS"
echo "=============================="
echo ""

echo "1. Checking local code changes..."
echo "---"
grep -n "useState<number | null>(null)" admin-ui/pages/homework-upload.tsx && echo "✅ Countdown null initialization found" || echo "❌ Countdown initialization not found"
echo ""

echo "2. Checking backend phone validation..."
echo "---"
grep -n "if not student.phone_number:" api/routes/homework.py && echo "✅ Phone validation found" || echo "❌ Phone validation missing"
echo ""

echo "3. Checking Celery task logging..."
echo "---"
grep -n "Starting homework submission confirmation task" tasks/celery_tasks.py && echo "✅ Enhanced logging found" || echo "❌ Logging not found"
echo ""

echo "4. Checking git status..."
echo "---"
git log --oneline -1
echo ""

echo "5. Checking if frontend built successfully..."
echo "---"
if [ -d "admin-ui/.next" ]; then
    echo "✅ Frontend build directory exists"
    ls -la admin-ui/.next/ | head -5
else
    echo "⚠️  Frontend build directory not found - may need to rebuild"
fi
echo ""

echo "6. Checking environment variables..."
echo "---"
echo "NEXT_PUBLIC_API_URL: ${NEXT_PUBLIC_API_URL:-(not set - will use fallback)}"
echo ""

echo "7. Summary:"
echo "---"
echo "If production isn't working:"
echo "1. Railway may not have deployed yet - check Railway dashboard"
echo "2. Browser cache - try Ctrl+Shift+Delete or open in incognito"
echo "3. Check browser console (F12) for JavaScript errors"
echo "4. Check backend logs in Railway for confirmation task issues"
