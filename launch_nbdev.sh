echo '========== 🏗 build unpackai *.py files =========='
nbdev_build_lib
echo '========== ✅  =========='
echo '========== 🧼 clean notebooks =========='
nbdev_clean_nbs
# We want to have a README managed independently
echo '========== ✅  =========='
echo "========== 🧪 extract tests under $(dirname $0) =========="
# Extract Test Cases
cd $(dirname "$0")=
python3 test/test_extractor.py
echo '========== ✅  =========='
# Reinstall the package
echo '========== 📦 reinstall unpackai =========='
pip install -e .
echo '========== ✅  =========='

