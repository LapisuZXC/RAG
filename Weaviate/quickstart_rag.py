import weaviate

client = weaviate.connect_to_local()
try:
    questions = client.collections.get("Question")

    response = questions.generate.near_text(
        query="biology",
        limit=2,
        grouped_task="Write a tweet with emojis about these facts."
    )

    print(response.generated)  # Inspect the generated text
    
except Exception as e:
    print(e)

finally:
    client.close()  # Free up resources