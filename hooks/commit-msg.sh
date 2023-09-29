#!/usr/bin/env bash

print_title() {
    TIT='\033[1;33m'
    NCL='\033[0m'
    title=$1

    set -e

    echo -e
    echo -e "${TIT}${title}${NCL}"
    echo -e
}

print_title "Linting Commit"

npx commitlint --edit