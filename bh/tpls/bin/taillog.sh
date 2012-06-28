#!/bin/sh
BASE={{ base }}
tail -f $BASE/logs/* $BASE/logs/*/*
