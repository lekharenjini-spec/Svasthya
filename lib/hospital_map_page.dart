 import 'package:flutter/material.dart';

import 'hospital_map.dart';
import 'hospital_map_data.dart';

class HospitalMapPage extends StatelessWidget {
  const HospitalMapPage({super.key});

  void showHospitalDetails(
    BuildContext context,
    HospitalLocation hospital,
  ) {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                hospital.name,
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 10),
              Text('Address: ${hospital.address}'),
              const SizedBox(height: 10),
              Text('Phone: ${hospital.phone}'),
            ],
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Find Hospitals'),
        backgroundColor: Colors.green,
      ),
      body: HospitalMap(
        hospitals: hospitalLocations,
        onHospitalTap: (hospital) {
          showHospitalDetails(context, hospital);
        },
      ),
    );
  }
}