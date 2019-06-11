#!/bin/bash

set -e

# Exec the specified command or fall back on bash
if [ $# -eq 0 ]; then
    cmd=bash
else
    cmd=$*
fi

run-hooks () {
    # Source scripts or run executable files in a directory
    if [[ ! -d "$1" ]] ; then
	return
    fi
    echo "$0: running hooks in $1"
    for f in "$1"/*; do
	case "$f" in
	    *.sh)
		echo "$0: running $f"
		source "$f"
		;;
	    *)
		if [[ -x "$f" ]] ; then
		    echo "$0: running $f"
		    "$f"
		else
		    echo "$0: ignoring $f"
		fi
		;;
	esac
    echo "$0: done running hooks in $1"
    done
}

# Execute the command
run-hooks /usr/local/bin/before-notebook.d
echo "Executing the command: $cmd"
exec $cmd
