import json

print("=== Testing recommendation_chunks.json ===")

with open("recommendation_chunks.json", "r", encoding="utf-8") as f:
    recommendations = json.load(f)

print("Type:", type(recommendations).__name__)
print("Count:", len(recommendations))

if len(recommendations) > 0:
    print("First item:")
    print(recommendations[0])


print("\n=== Testing table_chunks.json ===")

with open("table_chunks.json", "r", encoding="utf-8") as f:
    tables = json.load(f)

print("Type:", type(tables).__name__)
print("Count:", len(tables))

if len(tables) > 0:
    print("First item:")
    print(tables[0])


print("\n=== TEST COMPLETED ===")