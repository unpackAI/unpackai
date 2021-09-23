nbdev_build_lib
nbdev_clean_nbs
# We want to have a README managed independently
nbdev_build_docs --mk_readme False
# Extract Test Cases
cd $(dirname "$0")
python3 test/extract_tests.py
