#!/usr/bin/bash

# read from /etc
os_release=$(grep PRETTY_NAME /etc/os-release)
# extract quoted fields
os_release=${os_release#*=\"}
os_release=${os_release%\"}
# replace whitespace with slash
os_release=${os_release//[[:space:]]/-}

# read hardware information from lscpu
arch=$(lscpu | grep Architecture)
arch=${arch#*:}
arch=${arch//[[:space:]]/}
model_name=$(lscpu | grep "^[[:space:]]*Model name:")
model_name=${model_name##* }
cpu_count=$(lscpu | grep "^[[:space:]]*CPU(s):")
cpu_count=${cpu_count##* }
socket_count=$(lscpu | grep "^[[:space:]]*Socket(s):")
socket_count=${socket_count##* }

# put all pieces together
platform_info="${model_name}.${socket_count}P${cpu_count}C.${arch}.$os_release"
echo $platform_info
