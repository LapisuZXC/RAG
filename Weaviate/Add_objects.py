import weaviate

client = weaviate.connect_to_local()
try:
    source_objects = [
        {"title": "The Shawshank Redemption", "description": "A wrongfully imprisoned man forms an inspiring friendship while finding hope and redemption in the darkest of places."},
        {"title": "The Godfather", "description": "A powerful mafia family struggles to balance loyalty, power, and betrayal in this iconic crime saga."},
        {"title": "The Dark Knight", "description": "Batman faces his greatest challenge as he battles the chaos unleashed by the Joker in Gotham City."},
        {"title": "Jingle All the Way", "description": "A desperate father goes to hilarious lengths to secure the season's hottest toy for his son on Christmas Eve."},
        {"title": "A Christmas Carol", "description": "A miserly old man is transformed after being visited by three ghosts on Christmas Eve in this timeless tale of redemption."}
    ]

    collection = client.collections.get("DemoCollection")

    with collection.batch.dynamic() as batch:
        for src_obj in source_objects:
            # The model provider integration will automatically vectorize the object
            batch.add_object(
                properties={
                    "title": src_obj["title"],
                    "description": src_obj["description"],
                },
                # vector=vector  # Optionally provide a pre-obtained vector
            )
            if batch.number_errors > 10:
                print("Batch import stopped due to excessive errors.")
                break

    failed_objects = collection.batch.failed_objects
    if failed_objects:
        print(f"Number of failed imports: {len(failed_objects)}")
        print(f"First failed object: {failed_objects[0]}")

except Exception as e:
    print(e)
finally:
    client.close()  # Free up resources