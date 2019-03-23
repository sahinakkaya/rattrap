#!/usr/bin/env bash

keycode=$1
keycode=$(printf "%3s" "${keycode}")

xmodmap -pke | grep -e "keycode ${keycode}" | cut -d' ' -f "5 6"
