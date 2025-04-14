#!/bin/bash

# Obtenha um token de acesso para autenticação
ACCESS_TOKEN=$(curl -k -s -X POST "${KEYCLOAK_URL}/realms/master/protocol/openid-connect/token" \
  -d "username=${ADMIN_USERNAME}" \
  -d "password=${ADMIN_PASSWORD}" \
  -d "client_id=${CLIENT_ID}" \
  -d "grant_type=password" \
  -d "scope=offline_access" | jq -r .access_token)

# Verifique se o token foi obtido com sucesso
if [[ -z "$ACCESS_TOKEN" ]]; then
  echo "Erro ao obter o token de acesso."
  exit 1
fi

echo "Token de acesso obtido com sucesso."

# Crie o realm
curl -k -s -X POST "${KEYCLOAK_URL}/admin/realms" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d @${REALM_FILE}

echo "Realm criado com sucesso!"
