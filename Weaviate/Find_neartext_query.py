import weaviate

# There are also a completed RAG system can be added
# https://weaviate.io/developers/weaviate/quickstart/local

client = weaviate.connect_to_local()

try:
    collection = client.collections.get("DemoCollection")

    response = collection.query.near_text(
        query="A holiday film",  # The model provider integration will automatically vectorize the query
        limit=2
    )

    for obj in response.objects:
        print(obj.properties["title"])
        #print(f'Name: {obj.properties["title"]} \n Description: {obj.properties["description"]} \n\n')
        
except Exception as e:
    print(e)

finally:
    client.close()  # Free up resources