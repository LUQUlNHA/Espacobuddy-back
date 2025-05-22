#!/bin/bash

# -----------------------------------------------------------------------------
# ⚠️ Este script é utilizado exclusivamente para gerar uma pequena massa de dados
#    no banco de dados, com o objetivo de facilitar testes em ambientes de
#    desenvolvimento e produção. Não deve ser usado para populações definitivas.
# -----------------------------------------------------------------------------

SCRIPT_PATH=$(dirname $(readlink -f $0))"/assets/keycloak/"
. ${SCRIPT_PATH}tools/server-definitions.sh  # Importa variáveis de ambiente

. ${SCRIPT_PATH}tools/create-realm.sh        # Cria o realm padrão no Keycloak

. ${SCRIPT_PATH}curls/create_user.sh         # Cria um ou mais usuários via API

# KC = poek xpji sybn lwya
