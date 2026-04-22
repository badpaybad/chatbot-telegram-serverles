import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:flutter/foundation.dart';

class FileService extends ChangeNotifier {
  
  // Save an image file (e.g., for face recognition or user photos)
  Future<String> saveImage(File file, String fileName) async {
    final directory = await getApplicationDocumentsDirectory();
    final photosDir = Directory('${directory.path}/photos');
    
    if (!await photosDir.exists()) {
      await photosDir.create(recursive: true);
    }
    
    final path = '${photosDir.path}/$fileName';
    await file.copy(path);
    return path;
  }

  // Save temporary data to cache
  Future<void> saveToCache(String fileName, String content) async {
    final directory = await getTemporaryDirectory();
    final file = File('${directory.path}/$fileName');
    await file.writeAsString(content);
  }

  // Read data from cache
  Future<String?> readFromCache(String fileName) async {
    try {
      final directory = await getTemporaryDirectory();
      final file = File('${directory.path}/$fileName');
      if (await file.exists()) {
        return await file.readAsString();
      }
    } catch (e) {
      debugPrint('Error reading cache: $e');
    }
    return null;
  }

  // Get application documents path
  Future<String> getDocsPath() async {
    final directory = await getApplicationDocumentsDirectory();
    return directory.path;
  }

  // Delete a file
  Future<void> deleteFile(String path) async {
    final file = File(path);
    if (await file.exists()) {
      await file.delete();
    }
  }
}
