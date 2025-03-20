import weaviate
from weaviate.classes.config import Configure

client = weaviate.connect_to_local()

try:
    client.collections.create(
    "DemoCollection",
    vectorizer_config=[
        Configure.NamedVectors.text2vec_transformers(
            name="title_vector",
            source_properties=["title"],
        )
    ],
)
except Exception as e:
    print(e)
finally:
    client.close()  # Free up resources