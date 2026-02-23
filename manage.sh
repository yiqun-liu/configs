#!/usr/bin/env bash

# Color codes
BLUE='\033[34m'
YELLOW='\033[33m'
GREEN='\033[32m'
NC='\033[0m' # No Color

# ============================================================================
# Function Definitions
# ============================================================================

# Compare two files (non-recursive)
compare_files() {
	local file1="$1"
	local file2="$2"
	diff -u --color=auto "$file1" "$file2" || true
}

# Compare two directories (recursive with gitignore support)
compare_dirs() {
	local dir1="$1"
	local dir2="$2"

	# Get list of ignored files using git check-ignore
	ignored_files=$(cd "$dir2" && git check-ignore -r . 2>/dev/null | sed 's|^|./|' || true)

	if test -n "$ignored_files"
	then
		# Create temp file with exclude patterns
		exclude_file=$(mktemp)
		echo "$ignored_files" | while IFS= read -r f; do
			# Convert to glob pattern for exclude
			echo "*$f"
		done > "$exclude_file"

		# Use diff with excludes
		diff -u -r --color=auto --exclude-from="$exclude_file" "$dir1" "$dir2" || true
		rm -f "$exclude_file"
	else
		# No ignored files, run diff normally
		diff -u -r --color=auto "$dir1" "$dir2" || true
	fi
}

# Compare two paths (file or directory)
compare_paths() {
	local path1="$1"
	local path2="$2"

	if test -f "$path1" && test -f "$path2"
	then
		# Both are files
		compare_files "$path1" "$path2"
	elif test -d "$path1" && test -d "$path2"
	then
		# Both are directories
		compare_dirs "$path1" "$path2"
	else
		# Type mismatch (file vs directory)
		diff -u --color=auto "$path1" "$path2" || true
	fi
}

# ============================================================================
# Setup
# ============================================================================

repo_dir=`dirname $0`
repo_dir=`realpath $repo_dir`
order=$1

# check_parameters
if [[ $# -ne 1 || ( $order != "collect" && $order != "deploy" && $order != "compare" ) ]]
then
	echo "Expect one command argument: [collect|deploy|compare]"
	exit 1
fi

track_config_path=$repo_dir/tracked-configs
if ! test -e $track_config_path
then
	echo "Tracked configs not found. Please put configurations at path $track_config_path."
	echo "You could customize your settings based on $repo_dir/traced_configs.example."
	exit 1
fi

set -e

source $track_config_path

# ============================================================================
# Main Execution
# ============================================================================

echo start $order:
for mapping in "${mappings[@]}"
do
	# seperate fields with the default IFS (whitespace)
	read config_name target_path <<< $mapping
	repo_path=$repo_dir/$config_name

	if test $order == "collect"
	then
		echo -e "${BLUE}$config_name: $target_path --> $repo_path${NC}"
		rm -rf $repo_path
		cp -r $target_path $repo_path
	elif test $order == "deploy"
	then
		# Note: read -p doesn't support colors, so use echo + read workaround
		echo -en "${BLUE}deploy: $config_name --> $target_path? (y/n) ${NC}"
		read -n 1 choice
		while test $choice != 'y' && test $choice != 'n'
		do
			echo "Invalid choice: enter 'y' to confirm or 'n' to skip."
			echo -en "${BLUE}deploy: $config_name --> $target_path? (y/n) ${NC}"
			read -n 1 choice
		done

		if test $choice == 'y'
		then
			# When $target_path exists, direct copy will make $repo_path a
			# *sub*directory of $target_path.
			# Portable: remove target first, then copy (cp -T is GNU-only)
			mkdir -p "$(dirname "$target_path")"
			rm -rf "$target_path" && cp -r "$repo_path" "$target_path"
			echo -e "  ${GREEN}✓ copied: $config_name${NC}"
		else
			echo -e "  ${YELLOW}✗ skipped: $config_name${NC}"
		fi
	elif test $order == "compare"
	then
		echo -e "${BLUE}=== Comparing: $config_name ===${NC}"
		if test -e "$target_path" && test -e "$repo_path"
		then
			compare_paths "$target_path" "$repo_path"
		elif test -e "$target_path"
		then
			echo -e "${BLUE}Only in system: $target_path${NC}"
		elif test -e "$repo_path"
		then
			echo -e "${BLUE}Only in repo: $repo_path${NC}"
		fi
		echo ""
	fi
done

echo $order completed.
