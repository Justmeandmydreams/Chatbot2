# setup_cosmos.py
from azure.cosmos import CosmosClient, PartitionKey

client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)

# Create database
db = client.create_database_if_not_exists("chatbot-db")

# Create container
container = db.create_container_if_not_exists(
    id="conversations",
    partition_key=PartitionKey(path="/session_id"),
    offer_throughput=400
)
print("✅ Cosmos DB ready!")