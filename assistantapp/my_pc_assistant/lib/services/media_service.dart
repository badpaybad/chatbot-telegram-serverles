import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:image_picker/image_picker.dart';

class MediaService extends ChangeNotifier {
  final AudioRecorder _audioRecorder = AudioRecorder();
  final ImagePicker _imagePicker = ImagePicker();
  
  bool _isRecording = false;
  String? _lastRecordPath;
  File? _lastPickedImage;

  bool get isRecording => _isRecording;
  String? get lastRecordPath => _lastRecordPath;
  File? get lastPickedImage => _lastPickedImage;

  // --- Audio Recording ---

  Future<void> startRecording() async {
    try {
      if (await _audioRecorder.hasPermission()) {
        final directory = await getApplicationDocumentsDirectory();
        final path = '${directory.path}/record_${DateTime.now().millisecondsSinceEpoch}.m4a';
        
        const config = RecordConfig(); // Default config
        
        await _audioRecorder.start(config, path: path);
        _isRecording = true;
        notifyListeners();
      } else {
        debugPrint('Microphone permission denied');
      }
    } catch (e) {
      debugPrint('Error starting recording: $e');
    }
  }

  Future<String?> stopRecording() async {
    try {
      final path = await _audioRecorder.stop();
      _isRecording = false;
      _lastRecordPath = path;
      notifyListeners();
      return path;
    } catch (e) {
      debugPrint('Error stopping recording: $e');
      return null;
    }
  }

  // --- Image Picking/Camera ---

  Future<File?> pickImage(ImageSource source) async {
    try {
      final XFile? image = await _imagePicker.pickImage(
        source: source,
        imageQuality: 80,
      );
      
      if (image != null) {
        _lastPickedImage = File(image.path);
        notifyListeners();
        return _lastPickedImage;
      }
    } catch (e) {
      debugPrint('Error picking image: $e');
    }
    return null;
  }

  // --- Permissions ---

  Future<bool> requestPermissions() async {
    Map<Permission, PermissionStatus> statuses = await [
      Permission.microphone,
      Permission.camera,
      Permission.storage,
    ].request();
    
    return (statuses[Permission.microphone]?.isGranted ?? false) && 
           (statuses[Permission.camera]?.isGranted ?? false);
  }

  @override
  void dispose() {
    _audioRecorder.dispose();
    super.dispose();
  }
}
