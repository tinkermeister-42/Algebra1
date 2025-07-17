#!/bin/bash

set -e

echo "🚚 Preparing to deploy..."

# Build the book
~/.venv/bin/jupyter-book build .

BUILD_DIR="_build/html"

if [ ! -d "$BUILD_DIR" ]; then
  echo "❌ Build output not found in $BUILD_DIR"
  exit 1
fi

TEMP_DIR="_deploy_temp"
rm -rf "$TEMP_DIR"
mkdir "$TEMP_DIR"
cp -r "$BUILD_DIR"/* "$TEMP_DIR/"

# Switch to gh-pages branch
echo "📁 Switching to gh-pages branch..."
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
git checkout gh-pages

# Only clean out HTML files, NOT repo files
echo "🧹 Cleaning old HTML content..."
rm -rf *

# Copy new build
cp -r "$TEMP_DIR"/* .

# Add .nojekyll for GitHub Pages
touch .nojekyll

# Commit and push
echo "📦 Committing changes..."
git add .
git commit -m "Deploy updated book" || echo "No changes to commit"
git push origin gh-pages

# Switch back
echo "🔙 Switching back to $CURRENT_BRANCH..."
git checkout "$CURRENT_BRANCH"

# Cleanup
rm -rf "$TEMP_DIR"

echo "✅ Deployment complete!"
