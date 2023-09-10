#!/usr/bin/bash

repo_dir=`dirname $0`
repo_dir=`realpath $repo_dir`
order=$1

# check_parameters
if [[ $# -ne 1 || ( $order != "collect" && $order != "deploy" ) ]]
then
	echo "Expect one command argument: [collect|deploy]"
	exit -1
fi

track_config_path=$repo_dir/tracked-configs
if ! test -e $track_config_path
then
	echo "Tracked configs not found. Please put configurations at path $track_config_path."
	echo "You could customize your settings based on $repo_dir/traced_configs.example."
	exit -1
fi

set -e

source $track_config_path

echo start $order:
for mapping in "${mappings[@]}"
do
	# seperate fields with the default IFS (whitespace)
	read config_name config_dir <<< $mapping
	repo_config_dir=$repo_dir/$config_name

	if test $order == "collect"
	then
		echo "$config_name: $config_dir --> $repo_config_dir"
		rm -rf $repo_config_dir
		cp -r $config_dir $repo_config_dir
	elif test $order == "deploy"
	then
		read -p "deploy: $config_name --> $config_dir? (y/n) " choice
		while test $choice != 'y' && test $choice != 'n'
		do
			echo "Invalid choice: enter 'y' to confirm or 'n' to skip."
			read -p "deploy: $config_name --> $config_dir? (y/n) " choice
		done

		if test $choice == 'y'
		then
			# -T is necessary, otherwise when $config_dir exists, $repo_config_dir will
			# beome a *sub*directory of $config_dir.
			cp -r -T $repo_config_dir $config_dir
			echo "copied: $config_name --> $config_dir"
		else
			echo "skipped: $config_name"
		fi
	fi
done

echo $order completed.
