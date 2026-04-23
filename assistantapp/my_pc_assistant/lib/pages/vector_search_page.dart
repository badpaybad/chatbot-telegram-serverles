import 'dart:math';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/vector_db_service.dart';
import '../models/vector_data.dart';
import '../core/app_colors.dart';

class VectorSearchPage extends StatefulWidget {
  const VectorSearchPage({super.key});

  @override
  State<VectorSearchPage> createState() => _VectorSearchPageState();
}

class _VectorSearchPageState extends State<VectorSearchPage> {
  final _labelController = TextEditingController();
  final _searchController = TextEditingController();
  List<VectorData> _searchResults = [];

  // Giả lập tạo vector ngẫu nhiên (vì chúng ta chưa tích hợp model embedding thực tế)
  List<double> _generateRandomVector(int dim) {
    final random = Random();
    return List.generate(dim, (_) => random.nextDouble());
  }

  void _addData() {
    if (_labelController.text.isEmpty) return;
    
    final newData = VectorData(
      label: _labelController.text,
      embedding: _generateRandomVector(128), // 128 dimensions
    );
    
    context.read<VectorDbService>().addVectorData(newData);
    _labelController.clear();
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Đã thêm dữ liệu Vector vào ObjectBox')),
    );
    setState(() {});
  }

  void _search() {
    // Trong thực tế, query string phải được chuyển thành vector qua model embedding
    // Ở đây chúng ta giả lập bằng cách tạo vector ngẫu nhiên dựa trên query (seed)
    final queryVector = _generateRandomVector(128);
    final results = context.read<VectorDbService>().searchSimilar(queryVector, limit: 5);
    setState(() {
      _searchResults = results;
    });
  }

  @override
  Widget build(BuildContext context) {
    final vectorDb = context.watch<VectorDbService>();
    final allData = vectorDb.getAll();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Vector DB (ObjectBox)', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: AppColors.secondary,
        foregroundColor: AppColors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Thêm dữ liệu mới', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _labelController,
                    decoration: const InputDecoration(
                      hintText: 'Nhập nhãn dữ liệu (ví dụ: "User Profile A")',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                ElevatedButton(
                  onPressed: _addData,
                  style: ElevatedButton.styleFrom(backgroundColor: AppColors.secondary, foregroundColor: Colors.white),
                  child: const Text('Thêm'),
                ),
              ],
            ),
            const SizedBox(height: 30),
            const Text('Tìm kiếm tương đồng (Vector Search)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _searchController,
                    decoration: const InputDecoration(
                      hintText: 'Nhập nội dung tìm kiếm...',
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                ElevatedButton(
                  onPressed: _search,
                  style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary, foregroundColor: Colors.white),
                  child: const Text('Tìm'),
                ),
              ],
            ),
            const SizedBox(height: 20),
            Expanded(
              child: _searchResults.isEmpty 
                ? _buildDataList('Dữ liệu trong Database', allData)
                : _buildDataList('Kết quả tìm kiếm tương đồng', _searchResults),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          vectorDb.clear();
          setState(() => _searchResults = []);
        },
        backgroundColor: Colors.red,
        child: const Icon(Icons.delete_sweep, color: Colors.white),
      ),
    );
  }

  Widget _buildDataList(String title, List<VectorData> data) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(title, style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.grey)),
            if (_searchResults.isNotEmpty)
              TextButton(
                onPressed: () => setState(() => _searchResults = []),
                child: const Text('Clear Search'),
              ),
          ],
        ),
        const Divider(),
        Expanded(
          child: data.isEmpty 
            ? const Center(child: Text('Chưa có dữ liệu'))
            : ListView.builder(
                itemCount: data.length,
                itemBuilder: (context, index) {
                  final item = data[index];
                  return ListTile(
                    leading: const CircleAvatar(child: Icon(Icons.psychology)),
                    title: Text(item.label),
                    subtitle: Text('Vector: [${item.embedding?.take(3).join(", ") ?? ""} ...]'),
                    trailing: const Icon(Icons.chevron_right),
                  );
                },
              ),
        ),
      ],
    );
  }
}
