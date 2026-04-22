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
    final docsDir = await getApplicationDocumentsDirectory();
    final store = await openStore(directory: p.join(docsDir.path, "obx-db"));
    return ObjectBox._create(store);
  }
}
