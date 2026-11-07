import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import 'hospital_map_data.dart';

class HospitalMap extends StatelessWidget {
  final List<HospitalLocation> hospitals;
  final Function(HospitalLocation) onHospitalTap;

  const HospitalMap({
    super.key,
    required this.hospitals,
    required this.onHospitalTap,
  });

  @override
  Widget build(BuildContext context) {
    return FlutterMap(
      options: const MapOptions(
        initialCenter: LatLng(10.8505, 76.2711),
        initialZoom: 7,
      ),
      children: [
        TileLayer(
          urlTemplate:
              'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
          userAgentPackageName: 'com.example.swasthya',
        ),

        MarkerLayer(
          markers: hospitals.map((hospital) {
            return Marker(
              point: LatLng(
                hospital.latitude,
                hospital.longitude,
              ),
              width: 60,
              height: 60,
              child: IconButton(
                icon: const Icon(
                  Icons.location_on,
                  color: Colors.red,
                  size: 38,
                ),
                onPressed: () => onHospitalTap(hospital),
              ),
            );
          }).toList(),
        ),

        RichAttributionWidget(
          attributions: [
            TextSourceAttribution(
              '© OpenStreetMap contributors',
            ),
          ],
        ),
      ],
    );
  }
}
