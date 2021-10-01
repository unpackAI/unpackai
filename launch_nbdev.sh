echo '========== 🏗 build unpackai *.py files =========='
nbdev_build_lib
echo '========== ✅  =========='
echo '========== 🧼 clean notebooks =========='
nbdev_clean_nbs
# We want to have a README managed independently
echo '========== ✅  =========='
echo '========== 📚 build unpackai documentations =========='
nbdev_build_docs --mk_readme False
echo '========== ✅  =========='
echo "========== 🧪 extract tests under $(dirname $0) =========="
# Extract Test Cases
cd $(dirname "$0")
python3 test/extract_tests.py
echo '========== ✅  =========='
# Reinstall the package
echo '========== 📦 reinstall unpackai =========='
pip install -e .
echo '========== ✅  =========='