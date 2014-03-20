#!/bin/bash
sleep 5
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
rm -f $DIR/../Gen_III_Suite
mv $DIR/Gen_III_Suite $DIR/../
$DIR/../Gen_III_Suite
rm -fr $DIR
exit 0
