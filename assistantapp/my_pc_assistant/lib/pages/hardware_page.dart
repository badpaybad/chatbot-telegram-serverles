import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:image_picker/image_picker.dart';
import '../core/app_colors.dart';
import '../services/bluetooth_service.dart';
import '../services/nfc_service.dart';
import '../services/biometric_service.dart';
import '../services/connectivity_service.dart';
import '../services/device_service.dart';
import '../services/media_service.dart';

class HardwarePage extends StatefulWidget {
  const HardwarePage({super.key});

  @override
  State<HardwarePage> createState() => _HardwarePageState();
}

class _HardwarePageState extends State<HardwarePage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<DeviceService>().fetchAndroidVersion();
      context.read<ConnectivityService>().checkConnectivity();
    });
  }

  @override
  Widget build(BuildContext context) {
    final bluetoothService = context.watch<BluetoothService>();
    final nfcService = context.watch<NfcService>();
    final biometricService = context.watch<BiometricService>();
    final connectivityService = context.watch<ConnectivityService>();
    final deviceService = context.watch<DeviceService>();
    final mediaService = context.watch<MediaService>();

    final lastImage = mediaService.lastPickedImage;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Hardware Dashboard', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: AppColors.white,
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _buildInfoCard(
            title: 'Native Device Info',
            subtitle: 'Lấy từ Android Native Method Channel',
            content: deviceService.androidVersion,
            icon: Icons.android,
            color: Colors.green,
            onAction: () => deviceService.fetchAndroidVersion(),
            actionLabel: 'Refresh',
          ),
          _buildInfoCard(
            title: 'Biometrics',
            subtitle: 'Vân tay & Khuôn mặt',
            content: 'Chạm để kiểm tra khả năng hỗ trợ',
            icon: Icons.fingerprint,
            color: Colors.blue,
            onAction: () async {
              final can = await biometricService.canCheckBiometrics();
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text(can ? 'Thiết bị hỗ trợ sinh trắc học' : 'Không hỗ trợ sinh trắc học')),
                );
              }
            },
            actionLabel: 'Check',
          ),
          _buildInfoCard(
            title: 'Connectivity',
            subtitle: 'Trạng thái mạng',
            content: 'Trạng thái: ${connectivityService.connectionStatus}',
            icon: Icons.wifi,
            color: Colors.orange,
            onAction: () => connectivityService.checkConnectivity(),
            actionLabel: 'Refresh',
          ),
          _buildInfoCard(
            title: 'Bluetooth',
            subtitle: 'Quét thiết bị xung quanh',
            content: bluetoothService.isScanning ? 'Đang quét...' : '${bluetoothService.scanResults.length} thiết bị tìm thấy',
            icon: Icons.bluetooth,
            color: Colors.blueAccent,
            onAction: () => bluetoothService.isScanning ? bluetoothService.stopScan() : bluetoothService.startScan(),
            actionLabel: bluetoothService.isScanning ? 'Stop' : 'Scan',
          ),
          _buildInfoCard(
            title: 'NFC',
            subtitle: 'Giao tiếp gần',
            content: 'Dữ liệu: ${nfcService.nfcData.isEmpty ? "Chưa có dữ liệu" : nfcService.nfcData}',
            icon: Icons.nfc,
            color: Colors.purple,
            onAction: () => nfcService.startNfcSession(),
            actionLabel: 'Start Session',
          ),
          _buildInfoCard(
            title: 'Microphone',
            subtitle: 'Ghi âm giọng nói',
            content: mediaService.isRecording ? 'Đang ghi âm...' : 'File cuối: ${mediaService.lastRecordPath ?? "Chưa có"}',
            icon: Icons.mic,
            color: Colors.red,
            onAction: () => mediaService.isRecording ? mediaService.stopRecording() : mediaService.startRecording(),
            actionLabel: mediaService.isRecording ? 'Stop' : 'Record',
          ),
          _buildInfoCard(
            title: 'Camera',
            subtitle: 'Chụp ảnh từ thiết bị',
            content: lastImage != null ? 'Đã chụp ảnh: ${lastImage.path.split('/').last}' : 'Chưa có ảnh',
            icon: Icons.camera_alt,
            color: Colors.teal,
            onAction: () => mediaService.pickImage(ImageSource.camera),
            actionLabel: 'Take Photo',
          ),
          if (lastImage != null)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 10),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: SizedBox(
                  width: double.infinity,
                  height: 200,
                  child: Image.file(
                    lastImage,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) => const Center(child: Text('Lỗi hiển thị ảnh')),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildInfoCard({
    required String title,
    required String subtitle,
    required String content,
    required IconData icon,
    required Color color,
    required VoidCallback onAction,
    required String actionLabel,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 20),
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: color.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(icon, color: color),
                ),
                const SizedBox(width: 15),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                      Text(subtitle, style: const TextStyle(color: Colors.grey, fontSize: 12)),
                    ],
                  ),
                ),
                ElevatedButton(
                  onPressed: onAction,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: color,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                  ),
                  child: Text(actionLabel),
                ),
              ],
            ),
            const Divider(height: 30),
            Text(
              content,
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
            ),
          ],
        ),
      ),
    );
  }
}
