#!/bin/bash
# Bitespeed Identity Reconciliation Test Script

# Check if the API is running
echo "Testing health endpoint..."
curl http://localhost:5001/health

echo -e "\n\n---------- BASIC SCENARIOS ----------\n"

# Test 1: Create a new primary contact
echo -e "\nTest 1: Create a new primary contact"
curl -X POST http://localhost:5001/identify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lorraine@hillvalley.edu",
    "phoneNumber": "123456"
  }'

# Test 2: Create a secondary contact (same phone, different email)
echo -e "\n\nTest 2: Create a secondary contact (same phone, different email)"
curl -X POST http://localhost:5001/identify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "mcfly@hillvalley.edu",
    "phoneNumber": "123456"
  }'

# Test 3: Lookup with just email - primary contact
echo -e "\n\nTest 3: Lookup with just email - primary contact"
curl -X POST http://localhost:5001/identify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lorraine@hillvalley.edu"
  }'

# Test 4: Lookup with just email - secondary contact
echo -e "\n\nTest 4: Lookup with just email - secondary contact"
curl -X POST http://localhost:5001/identify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "mcfly@hillvalley.edu"
  }'

# Test 5: Lookup with just phone number
echo -e "\n\nTest 5: Lookup with just phone number"
curl -X POST http://localhost:5001/identify \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "123456"
  }'

echo -e "\n\n---------- LINKING PRIMARIES ----------\n"

# Test 6: Create a new separate primary contact
echo -e "\nTest 6: Create a new separate primary contact"
curl -X POST http://localhost:5001/identify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doc@hillvalley.edu",
    "phoneNumber": "919191"
  }'

# Test 7: Create another separate primary contact
echo -e "\n\nTest 7: Create another separate primary contact"
curl -X POST http://localhost:5001/identify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "biff@hillvalley.edu",
    "phoneNumber": "717171"
  }'

# Test 8: Link two primary contacts - this should convert one to secondary
echo -e "\n\nTest 8: Link two primary contacts (through phone)"
curl -X POST http://localhost:5001/identify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doc@hillvalley.edu",
    "phoneNumber": "717171"
  }'

# Test 9: Link two primary contacts - this should convert one to secondary
echo -e "\n\nTest 9: Link two primary contacts (through email)"
curl -X POST http://localhost:5001/identify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lorraine@hillvalley.edu",
    "phoneNumber": "919191"
  }'

# Test 10: Verify all contacts are now linked
echo -e "\n\nTest 10: Verify all contacts are linked by checking original primary"
curl -X POST http://localhost:5001/identify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lorraine@hillvalley.edu"
  }'

echo -e "\n\n---------- EDGE CASES ----------\n"

# Test 11: Try with a new contact with both new email and new phone
echo -e "\nTest 11: Create completely new contact"
curl -X POST http://localhost:5001/identify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jennifer@hillvalley.edu",
    "phoneNumber": "888888"
  }'

# Test 12: Try with multiple new information points
echo -e "\n\nTest 12: Try with complete secondary information"
curl -X POST http://localhost:5001/identify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "marty.mcfly@hillvalley.edu",
    "phoneNumber": "777777"
  }'

# Test 13: Link to the new contact created in Test 11
echo -e "\n\nTest 13: Link to newer contact"
curl -X POST http://localhost:5001/identify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jennifer@hillvalley.edu",
    "phoneNumber": "777777"
  }'

echo -e "\n\n---------- ERROR CASES ----------\n"

# Test 14: Invalid request with no email or phone
echo -e "\nTest 14: Invalid request - missing both email and phone"
curl -X POST http://localhost:5001/identify \
  -H "Content-Type: application/json" \
  -d '{}'

# Test 15: Invalid request with null values
echo -e "\n\nTest 15: Invalid request - null values"
curl -X POST http://localhost:5001/identify \
  -H "Content-Type: application/json" \
  -d '{
    "email": null,
    "phoneNumber": null
  }'

echo -e "\n\n---------- FINAL STATE ----------\n"

# Test 16: Check the state of the original primary contact
echo -e "\nTest 16: Check final state of original primary contact"
curl -X POST http://localhost:5001/identify \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lorraine@hillvalley.edu"
  }'

echo -e "\n\nTest complete!"