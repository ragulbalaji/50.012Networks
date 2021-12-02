#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]; then
  echo "Please run with sudo!"
  exit
fi

echo "Building LWIP stacks."
(
  cd lwip-tap
  ./configure
  make
)
(
  cd lwip-tap-defended
  ./configure
  make
)

echo "Destroying existing mininet topology..."
mn -c
