#!/bin/bash -x
#Import IRIS data from scm/meta/git project

export PATH=$PATH:/bin:/usr/bin:/usr/local/bin

WORKDIR=/tmp/iris_scm
PROJECT=meta
LOCKFILE=/tmp/iris_scm.lock
SYS_PROXY=/etc/sysconfig/proxy

IMPORT_SCM=import_scm.py
IMPORT_SNAPSHOT=download_snapshots.py

GITPATH=$(grep -E '^SCM_META_GIT_PATH = ".+"' /etc/iris/iris.conf | awk -F'"' '{print $2}')

set_proxy(){
    . $SYS_PROXY
    unset PROXY_ENABLED
    export $(grep '_PROXY=' $SYS_PROXY | grep -v '^#' | awk -F'=' '{print $1}')
    # Upper case is unsupported scheme on some programs such as wget, so set lower case too.
    for var in $(env | grep '_PROXY=' | awk -F'=' '{print $1}'); do
        lower=$(echo $var | tr 'A-Z' 'a-z')
        export $lower="${!var}"
    done
}

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

    if [ -z "$HTTP_PROXY" ]; then
        if [ -f $SYS_PROXY ]; then
            echo "$(date)|set proxy"
            set_proxy
        else
            echo "$SYS_PROXY file is not existed!"
        fi
    fi

    pull && cd $WORKDIR && $IMPORT_SCM $PROJECT/domains $PROJECT/git-trees
    $IMPORT_SNAPSHOT $WORKDIR
) 9>$LOCKFILE
echo "$(date)|import scm done"
