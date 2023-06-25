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
conventional-pre-commit build ci docs feat fix perf refactor revert test style wip .git/COMMIT_EDITMSG