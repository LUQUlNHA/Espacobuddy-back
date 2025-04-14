#!/bin/bash

SCRIPT_PATH=$(dirname $(readlink -f $0))"/assets/keycloak/"
. ${SCRIPT_PATH}tools/server-definitions.sh # Importando variaveis de ambiente

. ${SCRIPT_PATH}tools/create-realm.sh

. ${SCRIPT_PATH}curls/create_user.sh

# KC = poek xpji sybn lwya
