import 'package:path_provider/path_provider.dart';
import 'package:path/path.dart' as p;
import '../models/vector_data.dart';
import '../objectbox.g.dart'; // This will be generated

class ObjectBox {
  /// The Store of this app.
  late final Store store;

  ObjectBox._create(this.store);

  /// Create an instance of ObjectBox to use throughout the app.
  static Future<ObjectBox> create() async {
    try {
      print('ObjectBox: Getting documents directory...');
      final docsDir = await getApplicationDocumentsDirectory();
      print('ObjectBox: Docs dir: ${docsDir.path}');
      
      final dbPath = p.join(docsDir.path, "obx-db");
      print('ObjectBox: Opening store at $dbPath ...');
      
      final store = await openStore(directory: dbPath);
      print('ObjectBox: Store opened successfully.');
      
      return ObjectBox._create(store);
    } catch (e) {
      print('ObjectBox: Error in create(): $e');
      rethrow;
    }
  }
}
