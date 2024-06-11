#!/bin/bash

cd "$(dirname "$0")" || exit 1

build_lambda() {
  echo "Building $1"
  cd lambdas/"$1" || exit 1
  rm -rf ./publish
  mkdir -p ../publish
  cp -r . ../publish/
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt -t ../publish/
  mv ../publish ./publish
  cd publish || exit 1
  zip -r ../package.zip . 
  cd ..
  rm -rf ./publish/*
  mv package.zip ./publish/
}

build_lambda "queue_processor"
