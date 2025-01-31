import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import 'providers/auth_provider.dart';
import 'providers/category_provider.dart';
import 'providers/file_provider.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';
import 'services/api_service.dart';

// Updated color scheme to match the crypto dashboard
const Color primaryColor = Color(0xFF8B5CF6); // Purple
const Color accentColor = Color(0xFF3B82F6); // Blue
const Color backgroundColor = Color(0xFF1A1B23); // Dark background
const Color surfaceColor = Color(0xFF242632); // Slightly lighter surface
const Color textColor = Color(0xFFE2E8F0); // Light text

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider(
          create: (_) => ApiService(),
        ),
        ChangeNotifierProvider(
          create: (_) => FileProvider(),
        ),
        ChangeNotifierProvider(
          create: (context) => AuthProvider(
            context.read<ApiService>(),
          ),
        ),
        ChangeNotifierProvider(
          create: (context) => CategoryProvider(
            context.read<FileProvider>(),
          ),
        ),
      ],
      child: MaterialApp(
        title: 'Document Manager',
        debugShowCheckedModeBanner: false,
        theme: ThemeData.dark().copyWith(
          textTheme: GoogleFonts.poppinsTextTheme(ThemeData.dark().textTheme),
          colorScheme: const ColorScheme.dark(
            primary: primaryColor,
            secondary: accentColor,
            surface: surfaceColor,
            background: backgroundColor,
            onBackground: textColor,
          ),
          cardTheme: CardTheme(
            elevation: 12,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20),
            ),
            color: surfaceColor,
          ),
          appBarTheme: AppBarTheme(
            backgroundColor: backgroundColor,
            elevation: 0,
            titleTextStyle: GoogleFonts.poppins(
              fontSize: 24,
              fontWeight: FontWeight.w600,
              color: textColor,
            ),
          ),
          scaffoldBackgroundColor: backgroundColor,
          elevatedButtonTheme: ElevatedButtonThemeData(
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(30),
              ),
              backgroundColor: primaryColor,
              foregroundColor: textColor,
            ),
          ),
        ),
        home: Consumer<AuthProvider>(
          builder: (context, authProvider, _) {
            return authProvider.isAuthenticated
                ? const HomeScreen()
                : const LoginScreen();
          },
        ),
      ),
    );
  }
}
