echo '========== ๐ build unpackai *.py files =========='
nbdev_build_lib
echo '========== โ  =========='
echo '========== ๐งผ clean notebooks =========='
nbdev_clean_nbs
# We want to have a README managed independently
echo '========== โ  =========='
echo "========== ๐งช extract tests under $(dirname $0) =========="
# Extract Test Cases
cd $(dirname "$0")=
python3 test/test_extractor.py
echo '========== โ  =========='
# Reinstall the package
echo '========== ๐ฆ reinstall unpackai =========='
pip install -e .
echo '========== โ  =========='

