import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_database/firebase_database.dart';
import 'package:flutter/foundation.dart';

class DatabaseService extends ChangeNotifier {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  final FirebaseDatabase _realtime = FirebaseDatabase.instance;

  // Firestore methods
  Future<void> addDataToFirestore(String collection, Map<String, dynamic> data) async {
    await _firestore.collection(collection).add(data);
  }

  Stream<QuerySnapshot> getFirestoreStream(String collection) {
    return _firestore.collection(collection).snapshots();
  }

  // Realtime Database methods
  Future<void> writeToRealtime(String path, dynamic value) async {
    await _realtime.ref(path).set(value);
  }

  Stream<DatabaseEvent> getRealtimeStream(String path) {
    return _realtime.ref(path).onValue;
  }
}
