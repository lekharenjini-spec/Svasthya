 import 'package:flutter/material.dart';
 import 'package:flutter_localizations/flutter_localizations.dart';

 import 'l10n/app_localizations.dart';
 import 'hospital_map_page.dart';
 import 'emergency_page.dart';
 import 'splash_screen.dart';
 import 'login_screen.dart';
 import 'signup_screen.dart';
 import 'package:supabase_flutter/supabase_flutter.dart';


 Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Supabase.initialize(
    url: 'https://urskffdrrdiwrqycakiq.supabase.co/rest/v1/',
    publishableKey:  'sb_publishable_opvv4Zaev8qNF8356vwyqg_gPCK-BDv' ,
  );

  runApp(const MedicalApp());

}

class MedicalApp extends StatefulWidget {
  const MedicalApp({super.key});

  @override
  State<MedicalApp> createState() => _MedicalAppState();
}

class _MedicalAppState extends State<MedicalApp> {
  Locale selectedLocale = const Locale('en');

  void changeLanguage(Locale locale) {
    setState(() {
      selectedLocale = locale;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Swasthya',
      locale: selectedLocale,

      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],

      supportedLocales: AppLocalizations.supportedLocales,

      routes: {
        '/login': (context) => const LoginScreen(),
        '/signup': (context) => const SignupScreen(),
        '/home': (context) => HomePage(
          onLanguageChange: changeLanguage,
          selectedLocale: selectedLocale,
        ),
      },

      home: const SplashScreen(),
    );
  }
}

class HomePage extends StatelessWidget {
  final Function(Locale) onLanguageChange;
  final Locale selectedLocale;

  const HomePage({
    super.key,
    required this.onLanguageChange,
    required this.selectedLocale,
  });

  @override
  Widget build(BuildContext context) {
    final app = AppLocalizations.of(context)!;

    return Scaffold(
      appBar: AppBar(
        title: Text(app.appTitle),
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
      ),

      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),

        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 20),

            const Icon(
              Icons.health_and_safety,
              size: 90,
              color: Colors.teal,
            ),

            const SizedBox(height: 15),

            Text(
              app.welcome,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 23,
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 25),

            const Text(
              'Select Your Language',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),

            const SizedBox(height: 10),

            DropdownButton<Locale>(
              value: selectedLocale,
              isExpanded: true,

              items: const [
                DropdownMenuItem(
                  value: Locale('en'),
                  child: Text('English'),
                ),
                DropdownMenuItem(
                  value: Locale('ml'),
                  child: Text('മലയാളം'),
                ),
                DropdownMenuItem(
                  value: Locale('hi'),
                  child: Text('हिन्दी'),
                ),
                DropdownMenuItem(
                  value: Locale('ta'),
                  child: Text('தமிழ்'),
                ),
                DropdownMenuItem(
                  value: Locale('te'),
                  child: Text('తెలుగు'),
                ),
                DropdownMenuItem(
                  value: Locale('kn'),
                  child: Text('ಕನ್ನಡ'),
                ),
                DropdownMenuItem(
                  value: Locale('ur'),
                  child: Text('اردو'),
                ),
                DropdownMenuItem(
                  value: Locale('bn'),
                  child: Text('বাংলা'),
                ),
                DropdownMenuItem(
                  value: Locale('gu'),
                  child: Text('ગુજરાતી'),
                ),
                DropdownMenuItem(
                  value: Locale('mr'),
                  child: Text('मराठी'),
                ),
                DropdownMenuItem(
                  value: Locale('pa'),
                  child: Text('ਪੰਜਾਬੀ'),
                ),
                DropdownMenuItem(
                  value: Locale('or'),
                  child: Text('ଓଡ଼ିଆ'),
                ),
                DropdownMenuItem(
                  value: Locale('as'),
                  child: Text('অসমীয়া'),
                ),
              ],

              onChanged: (locale) {
                if (locale != null) {
                  onLanguageChange(locale);
                }
              },
            ),

            const SizedBox(height: 25),

            SizedBox(
              height: 60,
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const EmergencyPage(),
                    ),
                  );
                },
                icon: const Icon(Icons.sos, size: 28),
                label: const Text(
                  'SOS - Emergency Help',
                  style: TextStyle(fontSize: 18),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red,
                  foregroundColor: Colors.white,
                ),
              ),
            ),

            const SizedBox(height: 15),

            ElevatedButton.icon(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const HospitalMapPage(),
                  ),
                );
              },
              icon: const Icon(Icons.map),
              label: Text(app.findHospitals),
            ),

            const SizedBox(height: 12),

            ElevatedButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.medication),
              label: Text(app.medicineDelivery),
            ),

            const SizedBox(height: 12),

            ElevatedButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.mic),
              label: Text(app.voiceAssistant),
            ),
          ],
        ),
      ),
    );
  }
}
