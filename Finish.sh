#!/bin/bash
sleep 5
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ParentDIR="$(dirname "$dir")"
rm -f $DIR/../Gen_III_Suite
mv $DIR/Gen_III_Suite $DIR/../
rm $DIR/Finsh.sh
rm -fr $DIR/../tmp
$ParentDIR/Gen_III_Suite
exit 0
