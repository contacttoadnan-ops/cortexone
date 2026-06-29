from knowledge_index import KnowledgeIndex

index = KnowledgeIndex()

index.build()

print(index.stats())

index.save()

print("Knowledge index created.")