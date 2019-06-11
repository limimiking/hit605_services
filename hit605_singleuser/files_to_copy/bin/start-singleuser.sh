#!/bin/bash
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

set -e

# set default ip to 0.0.0.0
if [[ "$NOTEBOOK_ARGS $@" != *"--ip="* ]]; then
  NOTEBOOK_ARGS="--ip=0.0.0.0 $NOTEBOOK_ARGS"
fi

if [ ! -z "$JUPYTER_ENABLE_LAB" ]; then
  NOTEBOOK_BIN="jupyter labhub"
else
  NOTEBOOK_BIN=jupyterhub-singleuser
fi

. /usr/local/bin/start.sh $NOTEBOOK_BIN $NOTEBOOK_ARGS $@
