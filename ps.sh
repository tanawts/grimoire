#!/bin/bash

# Here is a mock-up of non-performant ps(1).

PROG_NAME="${0##*/}"

usage() {
    cat <<EOF
usage: ${PROG_NAME}

Faux \`ps uaxw' (without stats).

Options:
-p, --proc=<PATH>           path to /mounted/proc
-h, --help                  this useless garbage

EOF
    exit 1
}


GETOPT_TEMP=$(getopt --options p:h \
    --long proc:,help --name "${PROG_NAME}" -- "$@")

# (NB! quotes required to invoke GNU getopt(1) this way)
eval set -- "${GETOPT_TEMP}"

proc=/proc
while true; do
    case "$1" in
    -p|--proc)
        proc="$2"
        shift 2
        ;;
    -h|--help)
        usage
        ;;
    --)
        shift
        break
        ;;
    *)
        err "Getopt failed!"
        exit 1
        ;;
    esac
done

# make sure they gave us directory
# XXX  this won't verify that supplied dir is a /proc dir...
if [ ! -d "${proc}" ]; then
    >&2 echo "${PROG_NAME}: Not a directory: ${proc}"
    exit 1
fi

cd "${proc}"
echo -e "USER\tPID\tCOMMAND"  # print table header

ls -d [0-9]* |sort -n |while read pid; do
    cmd="$(tr '\0' ' ' < "${pid}/cmdline")"
    if [ -z "${cmd}" ]; then  # probably kernel thread
        usr=root
        cmd="[$(grep -iw name "${pid}/status" |sed "s/Name:\t//")]"
    else
        usr="$(stat -c %U "${pid}/cmdline")"
    fi
    echo -e "${usr}\t${pid}\t${cmd}"
done
