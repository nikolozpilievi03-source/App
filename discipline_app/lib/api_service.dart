import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // Change this to your IP!
  static const String baseUrl = 'http://10.0.2.2:8000';
  
  static Future<bool> testConnection() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/'));
      return response.statusCode == 200;
    } catch (e) {
      print('Connection test failed: $e');
      return false;
    }
  }
  
  static Future<List<Map<String, dynamic>>> getRoutines() async {
    try {
      print('📡 Fetching routines from: $baseUrl/routines');
      
      final response = await http.get(
        Uri.parse('$baseUrl/routines'),
        headers: {'Content-Type': 'application/json'},
      );
      
      print('📥 Response status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        print('✅ Loaded ${data.length} routines');
        return List<Map<String, dynamic>>.from(data);
      } else {
        throw Exception('Failed to load routines: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Error loading routines: $e');
      rethrow;
    }
  }
  
  static Future<void> createRoutine(Map<String, dynamic> routine) async {
    try {
      print('📤 Creating routine: ${routine['title']}');
      
      final response = await http.post(
        Uri.parse('$baseUrl/routines'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode([routine]),
      );
      
      print('📥 Response status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        print('✅ Routine created successfully');
      } else {
        throw Exception('Failed to create routine: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Error creating routine: $e');
      rethrow;
    }
  }
  
  static Future<void> completeRoutine(int id) async {
    try {
      print('📤 Completing routine: $id');
      
      final response = await http.post(
        Uri.parse('$baseUrl/routines/$id/complete'),
        headers: {'Content-Type': 'application/json'},
      );
      
      print('📥 Response status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        print('✅ Routine completed successfully');
      } else {
        throw Exception('Failed to complete routine: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Error completing routine: $e');
      rethrow;
    }
  }
  
  static Future<Map<String, dynamic>> getAddictionStats() async {
    try {
      print('📡 Fetching addiction stats from: $baseUrl/addiction-stats');
      
      final response = await http.get(
        Uri.parse('$baseUrl/addiction-stats'),
        headers: {'Content-Type': 'application/json'},
      );
      
      print('📥 Response status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        print('✅ Loaded addiction stats');
        return data;
      } else {
        throw Exception('Failed to load stats: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Error loading stats: $e');
      rethrow;
    }
  }
  
  static Future<void> deleteRoutine(int id) async {
    try {
      print('📤 Deleting routine: $id');
      
      final response = await http.delete(
        Uri.parse('$baseUrl/routines/$id'),
        headers: {'Content-Type': 'application/json'},
      );
      
      print('📥 Response status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        print('✅ Routine deleted successfully');
      } else {
        throw Exception('Failed to delete routine: ${response.statusCode}');
      }
    } catch (e) {
      print('❌ Error deleting routine: $e');
      rethrow;
    }
  }
}