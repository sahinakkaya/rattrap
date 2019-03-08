#!/bin/bash


# This is my first time trying to write bash script.
# So you may see crappy code...

# Don't panic, it is tested. It does not harm your computer but your brain cells :D


tmp_file=$(mktemp /tmp/xev_output.XXXXXX)

awk -F'[ )]+' -v RS='' '  BEGIN {
                                c=0
                          } /^KeyPress|^ButtonPress|^MappingNotify/ {
                                print
                                c=1
                          }
                          /^KeyRelease|^ButtonRelease/ {
                                if (c>0) {
                                    exit 0
                                }
                          } '  < <(xev) >> ${tmp_file};


awk -F'[ )]+' '             BEGIN {
                                mouse=0
                            }
                            /^KeyPress/ {
                            e=mouse?"ButtonPress":"KeyPress"
                            for (i=0;i<2;i++) {
                                getline
                            }
                            key=$8 " " $5
                            }
                            /^MappingNotify/ {
                                mouse= (mouse+1)%2
                                getline
                            }
                            /^ButtonPress/ {
                                e="ButtonPress"
                                for (i=0;i<2;i++) {
                                    getline
                                }
                                key=$4+$5
                            }
                            /state/ {
                                print e, key
                            }' ${tmp_file}

rm ${tmp_file};
