import 'package:flutter/foundation.dart';
import '../models/vector_data.dart';
import '../core/objectbox.dart';
import '../objectbox.g.dart';

class VectorDbService extends ChangeNotifier {
  final ObjectBox _objectbox;
  late final Box<VectorData> _vectorBox;

  VectorDbService(this._objectbox) {
    _vectorBox = _objectbox.store.box<VectorData>();
  }

  // Add vector data
  int addVectorData(VectorData data) {
    final id = _vectorBox.put(data);
    notifyListeners();
    return id;
  }

  // Get all vector data
  List<VectorData> getAll() {
    return _vectorBox.getAll();
  }

  // Simple label search
  List<VectorData> searchByLabel(String query) {
    final q = _vectorBox.query(VectorData_.label.contains(query)).build();
    final results = q.find();
    q.close();
    return results;
  }

  // Vector search (Similarity search)
  // This is what makes it a "Vector Database"
  List<VectorData> searchSimilar(List<double> queryVector, {int limit = 5}) {
    // Note: HNSW search requires a specific query type in ObjectBox
    // We use the query builder with nearest neighbors
    final query = _vectorBox
        .query(VectorData_.embedding.nearestNeighborsF32(queryVector, limit))
        .build();
    
    final results = query.find();
    query.close();
    return results;
  }

  // Delete data
  void delete(int id) {
    _vectorBox.remove(id);
    notifyListeners();
  }

  // Clear all
  void clear() {
    _vectorBox.removeAll();
    notifyListeners();
  }
}
