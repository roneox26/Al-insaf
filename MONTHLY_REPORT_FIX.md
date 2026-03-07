# Fix Applied for Monthly Report Error

## What was fixed:
1. ✓ Added `db.func.coalesce()` to all database sum() queries to handle NULL values
2. ✓ This prevents the scalar() error when there's no data
3. ✓ Removed excessive debug print statements that cause memory issues

## Deploy to Render.com:

### Option 1: Git Push (Recommended)
```bash
git add app.py
git commit -m "Fix monthly report scalar() error with coalesce"
git push origin main
```
Render will automatically deploy the changes.

### Option 2: Manual Deploy
1. Go to your Render.com dashboard
2. Select your web service
3. Click "Manual Deploy" > "Deploy latest commit"

## Test the fix:
1. Wait for deployment to complete (2-3 minutes)
2. Go to your app URL
3. Navigate to Monthly Report
4. The error should be resolved

## What caused the error:
- Database queries returning NULL when no data exists
- The `.scalar()` method fails on NULL values
- Worker was killed due to memory issues from excessive logging

## The fix:
- `db.func.coalesce(db.func.sum(...), 0)` returns 0 instead of NULL
- This prevents the scalar() error
- Removed debug print statements to reduce memory usage

## If error persists:
Run this in Render Shell:
```bash
python -c "from app import db, app; app.app_context().push(); db.create_all()"
```

Then restart the service.
