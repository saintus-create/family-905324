#!/bin/bash

# This script imports the saas-kit repository into family-905324
# Run this from your repository root when you have terminal access

echo "Starting import of saas-kit into family-905324..."

# Add the saas-kit remote
git remote add saas-kit https://github.com/saintus-create/saas-kit.git || true

# Fetch from saas-kit
echo "Fetching saas-kit repository..."
git fetch saas-kit main

# Merge saas-kit into current branch
echo "Merging saas-kit into your repository..."
git config user.name "SaaS Kit Import" || true
git config user.email "import@saaskit.local" || true

git merge --allow-unrelated-histories saas-kit/main -m "Import saas-kit template into family-905324"

echo "Import complete!"
echo "Now run: git push origin main"
