#!/bin/bash
echo "============================================================"
echo "  DIT UI TEST SUITE RUNNER (LOCAL ENVIRONMENT)"
echo "============================================================"
echo ""

source venv/bin/activate
BASE_URL="http://localhost:5001"

echo "Running TS-01: Sidebar Navigation..."
python3 testcases/ts01_sidebar_navigation.py $BASE_URL
echo ""

echo "Running TS-02: Post Composer..."
python3 testcases/ts02_post_composer.py $BASE_URL
echo ""

echo "Running TS-03: Post Cards..."
python3 testcases/ts03_post_cards.py $BASE_URL
echo ""

echo "Running TS-04: Authentication..."
python3 testcases/ts04_authentication.py $BASE_URL
echo ""

echo "Running TS-05: Settings..."
python3 testcases/ts05_settings.py $BASE_URL
echo ""

echo "Running TS-06: Profile..."
python3 testcases/ts06_profile.py $BASE_URL
echo ""

echo "============================================================"
echo "  ALL TEST SUITES COMPLETED"
echo "============================================================"
