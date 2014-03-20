#!/bin/bash
sleep 5
rm -f ../Gen_III_Suite
mv ./Gen_III_Suite ../
rm Finish.sh
rm -fr ../tmp
../Gen_III_Suite
exit 0
