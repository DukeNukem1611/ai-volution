import 'package:flutter/material.dart';
import 'package:mobile_app/main.dart';
import 'package:mobile_app/models/category.dart';
import 'package:mobile_app/screens/document_screen.dart';
import 'package:mobile_app/screens/news_screen.dart';
import 'package:mobile_app/screens/profile_screen.dart';
import 'package:provider/provider.dart';
import '../providers/category_provider.dart';
import '../providers/file_provider.dart';
import 'category_screen.dart';
import 'upload_screen.dart';
import 'package:google_fonts/google_fonts.dart';

// Replace the existing HomeScreen class with this:

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;
  final List<Widget> _screens = [
    const DocumentScreen(),
    const NewsScreen(),
    const ProfileScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.folder_outlined),
            selectedIcon: Icon(Icons.folder),
            label: 'Documents',
          ),
          NavigationDestination(
            icon: Icon(Icons.newspaper_outlined),
            selectedIcon: Icon(Icons.newspaper),
            label: 'News',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline),
            selectedIcon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}
