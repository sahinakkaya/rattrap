#!/usr/bin/env bash

keycode=$1
len=${#keycode}

if [[ ${len} != 3 ]]
then
  keycode=" "${keycode};
fi

xmodmap -pke | grep -e "keycode ${keycode}" | cut -d' ' -f "5 6"