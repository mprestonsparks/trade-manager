#!/bin/bash

# Download actionlint if not present
if ! command -v actionlint &> /dev/null; then
    echo "Downloading actionlint..."
    curl -s https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash | bash
fi

# Validate all workflow files
for file in *.yml; do
    echo "Validating $file..."
    actionlint "$file"
done
