#!/usr/bin/env bash

set -euo pipefail


ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_DIRETORY="${ROOT}/project"

rm -rf "$ROOT/build" # rm build files
scons -c # clean out c++ build files 

# build for host platform
scons