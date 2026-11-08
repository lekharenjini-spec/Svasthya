 
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import 'hospital_map_page.dart';

class EmergencyPage extends StatelessWidget {
  const EmergencyPage({super.key});

  Future<void> callEmergency(BuildContext context) async {
    final Uri phoneUri = Uri(
      scheme: 'tel',
      path: '112',
    );

    try {
      final bool opened = await launchUrl(phoneUri);

      if (!opened && context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Unable to open the phone dialler.'),
          ),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Calling is not supported on this device.'),
          ),
        );
      }
    }
  }

  Future<void> confirmEmergencyCall(BuildContext context) async {
    final bool? confirm = await showDialog<bool>(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: const Text('Emergency Call'),
          content: const Text(
            'Do you want to open the dialler for emergency number 112?',
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(dialogContext, false);
              },
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(dialogContext, true);
              },
              child: const Text('Continue'),
            ),
          ],
        );
      },
    );

    if (confirm == true && context.mounted) {
      await callEmergency(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Emergency Help'),
        backgroundColor: Colors.red,
        foregroundColor: Colors.white,
      ),

      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),

          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 20),

              const Icon(
                Icons.health_and_safety,
                color: Colors.red,
                size: 90,
              ),

              const SizedBox(height: 20),

              const Text(
                'How can we help you?',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),

              const SizedBox(height: 30),

              SizedBox(
                height: 60,
                child: ElevatedButton.icon(
                  onPressed: () {
                    confirmEmergencyCall(context);
                  },
                  icon: const Icon(Icons.phone),
                  label: const Text(
                    'Call Emergency 112',
                    style: TextStyle(fontSize: 17),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    foregroundColor: Colors.white,
                  ),
                ),
              ),

              const SizedBox(height: 20),

              SizedBox(
                height: 55,
                child: OutlinedButton.icon(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text(
                          'Ambulance search will be connected next.',
                        ),
                      ),
                    );
                  },
                  icon: const Icon(Icons.airport_shuttle),
                  label: const Text('Find Ambulance'),
                ),
              ),

              const SizedBox(height: 15),

              SizedBox(
                height: 55,
                child: OutlinedButton.icon(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) =>
                            const HospitalMapPage(),
                      ),
                    );
                  },
                  icon: const Icon(Icons.local_hospital),
                  label: const Text('Nearby Hospitals'),
                ),
              ),

              const SizedBox(height: 25),

              const Text(
                'Important: In India, 112 is the emergency response number. '
                'Use it for genuine emergencies.',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.black54,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
