import yaml
with open('.github/workflows/update-legal-feed.yml') as f:
    data = yaml.safe_load(f)
script = data['jobs']['update-feed']['steps'][1]['run']
script = script.replace("python - <<'PY'\n", "").replace("\nPY\n", "")
with open('scripts/update_legal_feed.py', 'w') as f:
    f.write(script)
