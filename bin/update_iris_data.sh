#!/bin/bash
#Import IRIS data from scm/meta/git project

export PATH=$PATH:/bin:/usr/bin:/usr/local/bin

WORKDIR=/tmp/iris_scm
PROJECT=meta
LOCKFILE=/tmp/iris_scm.lock

IMPORT_SCRIPT=import_scm.py

GITPATH=$(grep -E '^SCM_META_GIT_PATH = ".+"' /etc/iris/iris.conf | awk -F'"' '{print $2}')

pull() {
    if [ -d $PROJECT ]; then
        cd $PROJECT
        git reset --hard && git pull
    else
        git clone $GITPATH $PROJECT
    fi
}

# Main
echo "$(date)|import scm start"
(
    if ! flock -n 9; then
        echo "$(date)|cannot get the lock $LOCKFILE"
        exit 1
    fi

    if [ -z "$GITPATH" ]; then
        echo "$(date)|cannot get git path conf"
        exit 1
    fi
    echo "$(date)|gitpath|$GITPATH"

    mkdir -p $WORKDIR
    cd $WORKDIR

    pull && cd $WORKDIR && $IMPORT_SCRIPT $PROJECT/domains $PROJECT/git-trees
) 9>$LOCKFILE
echo "$(date)|import scm done"
