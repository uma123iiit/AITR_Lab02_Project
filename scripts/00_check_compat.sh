set -uo pipefail
mkdir -p logs
echo "== 1. resolver dry run (changes nothing) =="
pip install --dry-run -r requirements.txt 2>&1 | tee logs/pip_dryrun.txt | tail -15
echo "== 2. packages the resolver WOULD change that we do not want touched =="
grep -iE "would install.*(numpy|torch|scikit-learn|scipy)" logs/pip_dryrun.txt \
  && echo ">>> STOP: resolver wants to change a core package; paste logs/pip_dryrun.txt" \
  || echo "none flagged"