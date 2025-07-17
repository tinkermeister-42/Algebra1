#!/bin/bash

set -e

echo "🚚 Preparing to deploy..."

# Build the book
~/.venv/bin/jupyter-book build .

# Switch to gh-pages branch
echo "📁 Switching to gh-pages branch..."
git checkout gh-pages

# Clean out old files
echo "🧹 Cleaning old files..."
shopt -s extglob
rm -rf !(".git"|"."|".."|".gitignore"|".nojekyll")

# Copy new build
cp -r _build/html/* .

# Add .nojekyll so GitHub Pages will serve non-Jekyll content
touch .nojekyll

# Commit and push
echo "📦 Committing changes..."
git add .
git commit -m "Deploy updated book"
git push origin gh-pages

# Switch back
echo "🔙 Switching back to main branch..."
git checkout main

echo "✅ Deployment complete!"
