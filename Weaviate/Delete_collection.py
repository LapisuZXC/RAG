import weaviate
from weaviate.classes.config import Configure


client = weaviate.connect_to_local()

try:
    client.collections.delete("DemoCollection")  # THIS WILL DELETE THE SPECIFIED COLLECTION(S) AND THEIR OBJECTS

except Exception as e:
    print(e)
finally:
    client.close()  # Free up resources