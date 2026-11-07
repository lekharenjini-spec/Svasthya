 import 'package:flutter/material.dart';
 import 'hospital_map_page.dart'; 

void main() {
  runApp(const MedicalApp());
}

class MedicalApp extends StatelessWidget {
  const MedicalApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: const HomePage(),
    );
  }
}

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Medical Healthcare App"),
        backgroundColor: Colors.teal,
      ),

      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [

            const Icon(
              Icons.local_hospital,
              size: 90,
              color: Colors.teal,
            ),

            const SizedBox(height: 20),

            const Text(
              "Welcome to Healthcare",
              style: TextStyle(fontSize: 23),
            ),

            const SizedBox(height: 20),

            ElevatedButton(
              onPressed: () {},
              child: const Text("Find Hospitals"),
            ),

            ElevatedButton(
              onPressed: () {},
              child: const Text("Medicine Delivery"),
            ),

            ElevatedButton(
              onPressed: () {},
              child: const Text("Voice Assistant"),
            ),
          ],
        ),
      ),
    );
  }
}8
