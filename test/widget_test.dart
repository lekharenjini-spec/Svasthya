 import 'package:flutter_test/flutter_test.dart';
import 'package:svasthya_app/main.dart';

void main() {
testWidgets('Swasthya app loads successfully', (WidgetTester tester) async {
await tester.pumpWidget(const MedicalApp());

await tester.pump();

expect(find.byType(MedicalApp), findsOneWidget);

});
}