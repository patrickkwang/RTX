#!/usr/bin/env bash
# This script runs all the RTX Behave tests and uploads the JSON-formatted results to our S3 bucket. It clones the
# testing repo (if not already present) and saves the JSON report into whatever directory it is run from.

echo -e "\n=================== STARTING SCRIPT ===================\n"

REPORT_NAME="rtx-test-harness-report.json"
TESTING_REPO="translator-testing-framework"

echo -e "\nSETTING UP...\n"

# Create a local copy of the testing repo if we don't have one already
if [[ ! -d ${TESTING_REPO} ]]
then
    git clone --recursive https://github.com/RTXteam/translator-testing-framework.git
fi

# Start up a virtual environment for Behave and install requirements
python3 -m venv behave-env
source behave-env/bin/activate
cd ${TESTING_REPO}
git pull origin master
pip install -r requirements.txt

# Run all of our Behave tests, outputting a JSON report with results
echo -e "\nRUNNING RTX BEHAVE TESTS...\n"
behave -i rtx-tests.feature -f json.pretty -o ../${REPORT_NAME}
cd ..

# Direct user to the report in event of test failure
test_failed=$(grep -c failed ${REPORT_NAME})
if [[ ${test_failed} -gt 0 ]]
then
    echo -e "\nOne or more tests failed! Examine '${REPORT_NAME}' to see which tests."
else
    echo -e "\nAll tests passed!"
fi

# Upload the report to our S3 bucket
echo -e "\nUPLOADING REPORT TO S3...\n"
aws s3 cp --no-progress --region us-west-2 ${REPORT_NAME} s3://rtx-kg2-versioned/

echo -e "\n=================== SCRIPT FINISHED ===================\n"