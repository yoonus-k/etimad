import json

with open('all_tenders.json', encoding='utf-8') as f:
    data = json.load(f)
    
print(f"Tenders in file: {len(data['data'])}")
print(f"Total count from API: {data['totalCount']}")
print(f"Page size: {data['pageSize']}")
