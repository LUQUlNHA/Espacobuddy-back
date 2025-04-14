#!/bin/bash

URL="localhost:8080"


# Obter o token administrativo e armazená-lo na variável TOKEN
TOKEN=$(curl -k -X POST "http://$URL/realms/master/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=admin-cli" \
  -d "username=admin" \
  -d "password=admin" \
  -d "grant_type=password" | jq -r '.access_token')

# Usar o token para criar um novo usuário com a ação de verificação de e-mail
curl -k -X POST "http://$URL/admin/realms/espaco-buddy/users" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "username": "nicolas",
    "email": "nicolasbarsalini2017@gmail.com",
    "enabled": true,
    "requiredActions": ["VERIFY_EMAIL"]
  }'
  
USER_ID=$(curl -k -X GET "http://$URL/admin/realms/espaco-buddy/users?email=nicolasbarsalini2017@gmail.com" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.[0].id')

# Cria uma senha pro usuário
curl -k -X PUT "http://$URL/admin/realms/espaco-buddy/users/${USER_ID}/reset-password" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "type": "password",
    "value": "Nickjiu2004@",
    "temporary": false
  }'