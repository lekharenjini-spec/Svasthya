 import 'dart:convert';
import 'package:http/http.dart' as http;

class ChatbotService {
  // Replace this with your deployed backend URL.
  static const String backendUrl =
      'https://YOUR_PROJECT_REF.supabase.co/functions/v1/swasthya-chat';

  // Public Supabase anon/publishable key, NOT your secret service-role key.
  static const String supabaseKey = 'YOUR_SUPABASE_PUBLISHABLE_KEY';

  Future<String> sendMessage({
    required String message,
    required List<Map<String, String>> history,
  }) async {
    try {
      final response = await http.post(
        Uri.parse(backendUrl),
        headers: {
          'Content-Type': 'application/json',
          'apikey': supabaseKey,
          'Authorization': 'Bearer $supabaseKey',
        },
        body: jsonEncode({
          'message': message,
          'history': history,
        }),
      ).timeout(const Duration(seconds: 45));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['reply'] ?? 'Sorry, I could not understand.';
      }

      throw Exception(
        'Server error: ${response.statusCode} ${response.body}',
      );
    } catch (e) {
      throw Exception('Unable to connect to Swasthya AI: $e');
    }
  }
}