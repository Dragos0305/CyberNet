#!/bin/bash
exec apache2-foreground 
wait -n
exit $?
