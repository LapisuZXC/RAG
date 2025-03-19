import weaviate
import json

volume_query=input("Write a query: ")


client = weaviate.connect_to_local()
try:
    questions = client.collections.get("Question")

    response = questions.query.near_text(
        query=volume_query,
        limit=3
    )

    for obj in response.objects:
        print(json.dumps(obj.properties, indent=2))

except Exception as e:
    print(e)

finally:
    client.close()  # Free up resources