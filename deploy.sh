#!/bin/bash

set -e  # Stop on error

BUILD_DIR="_build/html"
DEPLOY_TEMP="/tmp/deploy_temp_jupyterbook"
JUPYTER_BOOK="$HOME/.venv/bin/jupyter-book"

echo "🔨 Building the book..."
$JUPYTER_BOOK build .

if [ ! -d "$BUILD_DIR" ]; then
  echo "❌ Build failed: $BUILD_DIR not found."
  exit 1
fi

echo "🚚 Preparing to deploy..."

# Clean and prepare temp deploy folder outside the repo
rm -rf "$DEPLOY_TEMP"
mkdir "$DEPLOY_TEMP"

cp -r "$BUILD_DIR"/* "$DEPLOY_TEMP"
touch "$DEPLOY_TEMP/.nojekyll"

echo "📁 Switching to gh-pages branch..."
git checkout gh-pages

# Remove everything EXCEPT .git and .vscode
echo "🧹 Cleaning old files (preserving .git, .vscode)..."
find . -mindepth 1 -maxdepth 1 ! -name '.git' ! -name '.vscode' ! -name 'deploy.sh' -exec rm -rf {} +

# Copy new build files in
cp -r "$DEPLOY_TEMP"/* .

echo "✅ Committing and pushing..."
git add .
git commit -m "Deploy updated site"
git push origin gh-pages

echo "🧽 Cleaning temp files..."
rm -rf "$DEPLOY_TEMP"

echo "🌐 Done! Your site should be live shortly."
