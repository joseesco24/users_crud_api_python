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

# ** info: fetching changed files list
staged_files=($(git diff --name-only --cached))
changed_files_count=${#staged_files[@]}
cero_element=${staged_files[0]}

# ** info: printing changed files list
if ([ $changed_files_count != 0 ] && [ "$cero_element" != "" ]); then
    print_title "Changed Files Count On This Commit"
    printf 'files in stage area: %i' $changed_files_count
    echo -e
    print_title "Changed Files List On This Commit"
    for staged_file in "${staged_files[@]}"; do
        echo $staged_file
    done
else
    print_title "There Are Not Changed Files On This Commit"
fi

# ** info: formatting files
print_title "Formatting Files"
npm run format

# ** info: updating staged files
if ([ $changed_files_count != 0 ] && [ "$cero_element" != "" ]); then
    for staged_file in "${staged_files[@]}"; do
        if test -f "$staged_file"; then
            git add $staged_file
        fi
    done
fi

# ** info: linting files
print_title "Linting Files"
npm run lint

# ** info: linting files
print_title "Commit Sucessfully"
