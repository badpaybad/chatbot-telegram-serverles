import 'package:objectbox/objectbox.dart';

@Entity()
class VectorData {
  @Id()
  int id = 0;

  @Index()
  String label;

  // The embedding vector
  // ObjectBox supports HNSW index for Float32List
  @HnswIndex(dimensions: 512) // Default dimension, can be adjusted for Gemma/FastText
  @Property(type: PropertyType.floatVector)
  List<double>? embedding;

  String? metadata; // JSON string for extra info

  DateTime createdAt;

  VectorData({
    required this.label,
    this.embedding,
    this.metadata,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();
}
