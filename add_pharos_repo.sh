#!/bin/bash
# Add pharos repository to Neo Alexandria
# Run this script after getting your JWT token

echo -e "\033[0;36mAdding repository: https://github.com/ram-tewari/pharos\033[0m"
echo ""

# Prompt for JWT token
read -p "Enter your JWT token (from browser DevTools or login response): " token

if [ -z "$token" ]; then
    echo -e "\033[0;31mError: Token is required\033[0m"
    exit 1
fi

echo ""
echo -e "\033[0;33mSending request to API...\033[0m"

response=$(curl -s -w "\n%{http_code}" -X POST \
    "https://pharos.onrender.com/api/resources/ingest-repo" \
    -H "Authorization: Bearer $token" \
    -H "Content-Type: application/json" \
    -d '{"git_url": "https://github.com/ram-tewari/pharos"}')

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

echo ""

if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
    echo -e "\033[0;32m✓ Repository ingestion started successfully!\033[0m"
    echo ""
    echo -e "\033[0;36mResponse:\033[0m"
    echo "$body" | jq '.'
    echo ""
    echo -e "\033[0;33mThe repository is being processed in the background.\033[0m"
    echo -e "\033[0;33mThis may take a few minutes depending on repository size.\033[0m"
    
    task_id=$(echo "$body" | jq -r '.task_id')
    if [ "$task_id" != "null" ]; then
        echo ""
        echo -e "\033[1;37mCheck status with:\033[0m"
        echo -e "\033[0;90mcurl -H 'Authorization: Bearer $token' https://pharos.onrender.com/api/resources/ingest-status/$task_id\033[0m"
    fi
else
    echo -e "\033[0;31m✗ Error adding repository (HTTP $http_code):\033[0m"
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
    
    if [ "$http_code" -eq 401 ]; then
        echo ""
        echo -e "\033[0;33mYour token may be expired or invalid. Try logging in again.\033[0m"
    elif [ "$http_code" -eq 429 ]; then
        echo ""
        echo -e "\033[0;33mRate limit exceeded. Please wait a minute and try again.\033[0m"
    fi
fi
