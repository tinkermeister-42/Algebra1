#!/bin/bash

set -e

BUILD_DIR="_build/html"
DEPLOY_DIR=".deploy_temp"

echo "📘 Building the book..."
~/.venv/bin/jupyter-book build .

echo "🚛 Preparing deployment folder..."
rm -rf $DEPLOY_DIR
mkdir $DEPLOY_DIR
cp -r $BUILD_DIR/* $DEPLOY_DIR/

echo "📁 Switching to gh-pages branch..."
git stash push -m "temp stash before deploy"
git checkout gh-pages

echo "🧹 Cleaning old files..."
find . -maxdepth 1 ! -name '.' ! -name '.git' ! -name '.nojekyll' -exec rm -rf {} +

echo "📥 Copying new files..."
cp -r $DEPLOY_DIR/* .
touch .nojekyll

echo "📦 Committing and pushing..."
git add .
git commit -m "Deploy updated book"
git push origin gh-pages

echo "🔙 Returning to main branch..."
git checkout main
git stash pop || true

echo "✅ Deployment complete!"
