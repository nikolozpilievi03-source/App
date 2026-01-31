import 'package:flutter/material.dart';
import 'api_service.dart';
import 'calendar_widgets.dart';
import 'package:intl/intl.dart';
import 'enhanced_stats_screen.dart';

void main() {
  runApp(DisciplineApp());
}

// Custom Color Palette
class AppColors {
  static const darkBlue = Color(0xFF27374D);
  static const mediumBlue = Color(0xFF526D82);
  static const lightBlue = Color(0xFF9DB2BF);
  static const veryLightBlue = Color(0xFFDDE6ED);
  
  static const success = Color(0xFF10B981);
  static const warning = Color(0xFFF59E0B);
  static const error = Color(0xFFEF4444);
  
  static const white = Color(0xFFFFFFFF);
  static const black = Color(0xFF1F2937);
  static const gray = Color(0xFF6B7280);
}

class DisciplineApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Discipline App',
      theme: ThemeData(
        primaryColor: AppColors.darkBlue,
        scaffoldBackgroundColor: AppColors.veryLightBlue,
        colorScheme: ColorScheme.fromSeed(
          seedColor: AppColors.darkBlue,
          primary: AppColors.darkBlue,
          secondary: AppColors.mediumBlue,
          surface: AppColors.white,
        ),
        cardTheme: CardThemeData(
          color: AppColors.white,
          elevation: 4,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        appBarTheme: AppBarTheme(
          backgroundColor: AppColors.darkBlue,
          elevation: 0,
          centerTitle: false,
          titleTextStyle: TextStyle(
            color: AppColors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
          iconTheme: IconThemeData(color: AppColors.white),
        ),
        floatingActionButtonTheme: FloatingActionButtonThemeData(
          backgroundColor: AppColors.mediumBlue,
          foregroundColor: AppColors.white,
        ),
        bottomNavigationBarTheme: BottomNavigationBarThemeData(
          backgroundColor: AppColors.white,
          selectedItemColor: AppColors.darkBlue,
          unselectedItemColor: AppColors.gray,
          elevation: 8,
        ),
        useMaterial3: true,
      ),
      home: SplashScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

// Splash Screen
class SplashScreen extends StatefulWidget {
  @override
  _SplashScreenState createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  bool _isConnected = false;
  String _message = 'Connecting to backend...';

  @override
  void initState() {
    super.initState();
    _testConnection();
  }

  Future<void> _testConnection() async {
    await Future.delayed(Duration(seconds: 1));
    
    final connected = await ApiService.testConnection();
    
    setState(() {
      _isConnected = connected;
      _message = connected 
          ? 'Connected! ✅' 
          : 'Cannot connect to backend ❌\n\nMake sure Python server is running';
    });
    
    if (connected) {
      await Future.delayed(Duration(seconds: 1));
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => HomeScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.darkBlue,
      body: Center(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                _isConnected ? Icons.check_circle : Icons.sync,
                size: 80,
                color: AppColors.white,
              ),
              SizedBox(height: 24),
              Text(
                _message,
                style: TextStyle(color: AppColors.white, fontSize: 18),
                textAlign: TextAlign.center,
              ),
              if (!_isConnected && _message.contains('Cannot'))
                Padding(
                  padding: EdgeInsets.only(top: 24),
                  child: ElevatedButton(
                    onPressed: () {
                      setState(() {
                        _message = 'Retrying...';
                      });
                      _testConnection();
                    },
                    child: Text('Retry'),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

// Home Screen
class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;
  List<Map<String, dynamic>> _routines = [];
  bool _isLoading = true;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadRoutines();
  }

  Future<void> _loadRoutines() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });
    
    try {
      final routines = await ApiService.getRoutines();
      setState(() {
        _routines = routines;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load routines: $e';
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final List<Widget> screens = [
      _buildDashboard(),
      _buildStatsScreen(),
      _buildSettingsScreen(),
    ];

    return Scaffold(
      appBar: AppBar(
        title: Text(
          _selectedIndex == 0
              ? 'Today\'s Discipline'
              : _selectedIndex == 1
                  ? 'Statistics'
                  : 'Settings',
        ),
        actions: [
          if (_selectedIndex == 0)
            IconButton(
              icon: Icon(Icons.refresh),
              onPressed: _loadRoutines,
            ),
          Padding(
            padding: EdgeInsets.only(right: 16),
            child: Center(
              child: Icon(Icons.circle, color: AppColors.success, size: 12),
            ),
          ),
        ],
      ),
      body: screens[_selectedIndex],
      floatingActionButton: _selectedIndex == 0
          ? FloatingActionButton(
              onPressed: () => _showAddRoutineDialog(),
              child: Icon(Icons.add),
            )
          : null,
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        items: [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_rounded),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.bar_chart_rounded),
            label: 'Stats',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.settings_rounded),
            label: 'Settings',
          ),
        ],
      ),
    );
  }

  Widget _buildDashboard() {
    if (_isLoading) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(color: AppColors.mediumBlue),
            SizedBox(height: 16),
            Text('Loading routines...'),
          ],
        ),
      );
    }

    if (_errorMessage != null) {
      return Center(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, size: 64, color: AppColors.error),
              SizedBox(height: 16),
              Text(_errorMessage!, textAlign: TextAlign.center),
              SizedBox(height: 24),
              ElevatedButton(
                onPressed: _loadRoutines,
                child: Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }

    return Column(
      children: [
        // Calendar Button
        Container(
          padding: EdgeInsets.all(16),
          child: ElevatedButton.icon(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => MonthGridScreen(
                    onMonthSelected: (month) {
                      Navigator.push(
                        context,
                        PageRouteBuilder(
                          pageBuilder: (context, animation, secondaryAnimation) =>
                              MonthCalendarView(
                            initialMonth: month,
                            routines: _routines,
                            onDaySelected: (date) {
                              Navigator.pop(context);
                              Navigator.pop(context);
                              _showAddRoutineDialog(preselectedDate: date);
                            },
                          ),
                          transitionsBuilder:
                              (context, animation, secondaryAnimation, child) {
                            return SlideTransition(
                              position: Tween<Offset>(
                                begin: Offset(1.0, 0.0),
                                end: Offset.zero,
                              ).animate(animation),
                              child: child,
                            );
                          },
                        ),
                      );
                    },
                  ),
                ),
              );
            },
            icon: Icon(Icons.calendar_month),
            label: Text('📅 View Calendar'),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.mediumBlue,
              padding: EdgeInsets.symmetric(vertical: 16),
              minimumSize: Size(double.infinity, 50),
            ),
          ),
        ),

        // Existing routine list
        Expanded(
          child: _routines.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.check_circle_outline, size: 100, color: AppColors.lightBlue),
                      SizedBox(height: 20),
                      Text('No routines yet!', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                      SizedBox(height: 10),
                      Text('Tap + to add your first routine'),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadRoutines,
                  child: ListView.builder(
                    padding: EdgeInsets.all(16),
                    itemCount: _routines.length,
                    itemBuilder: (context, index) {
                      return _RoutineCard(
                        routine: _routines[index],
                        onComplete: () => _completeRoutine(_routines[index]['id']),
                        onEdit: () => _editRoutine(index),
                        onDelete: () => _deleteRoutine(index),
                      );
                    },
                  ),
                ),
        ),
      ],
    );
  }

  Widget _buildStatsScreen() {
  return EnhancedStatsScreen(routines: _routines);
}
  Widget _buildSettingsScreen() {
    return ListView(
      padding: EdgeInsets.all(16),
      children: [
        ListTile(
          leading: Icon(Icons.link, color: AppColors.mediumBlue),
          title: Text('Backend URL'),
          subtitle: Text(ApiService.baseUrl),
          trailing: Icon(Icons.circle, color: AppColors.success, size: 12),
        ),
      ],
    );
  }

  Future<void> _showAddRoutineDialog({DateTime? preselectedDate}) async {
  final titleController = TextEditingController();
  TimeOfDay selectedTime = TimeOfDay.now();
  String personality = 'hood';
  DateTime selectedDate = preselectedDate ?? DateTime.now();

  await showDialog(
    context: context,
    builder: (dialogContext) => StatefulBuilder(
      builder: (dialogContext, setDialogState) => AlertDialog(
        title: Text(preselectedDate != null
            ? 'Routine for ${DateFormat('MMM d, yyyy').format(preselectedDate)}'
            : 'Add Routine'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: titleController,
                decoration: InputDecoration(
                  labelText: 'Routine Name',
                  border: OutlineInputBorder(),
                ),
              ),
              SizedBox(height: 16),

              InkWell(
                onTap: () async {
                  final time = await showTimePicker(
                    context: dialogContext,
                    initialTime: selectedTime,
                  );
                  if (time != null) {
                    setDialogState(() => selectedTime = time);
                  }
                },
                child: InputDecorator(
                  decoration: InputDecoration(
                    labelText: 'Time',
                    border: OutlineInputBorder(),
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(selectedTime.format(dialogContext)),
                      Icon(Icons.access_time),
                    ],
                  ),
                ),
              ),

              SizedBox(height: 16),

              DropdownButtonFormField<String>(
                value: personality,
                decoration: InputDecoration(
                  labelText: 'AI Voice',
                  border: OutlineInputBorder(),
                ),
                items: const [
                  DropdownMenuItem(value: 'hood', child: Text('🔥 Hood')),
                  DropdownMenuItem(value: 'calm', child: Text('😌 Calm')),
                  DropdownMenuItem(value: 'strict', child: Text('💪 Strict')),
                  DropdownMenuItem(value: 'motivational', child: Text('🏆 Motivational')),
                ],
                onChanged: (v) => setDialogState(() => personality = v!),
              ),
            ],
          ),
        ),

        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(),
            child: Text('Cancel'),
          ),

          ElevatedButton(
            onPressed: () async {
              if (titleController.text.isEmpty) return;

              Navigator.of(dialogContext).pop(); // close form dialog

              showDialog(
                context: context,
                barrierDismissible: false,
                builder: (_) => Center(child: CircularProgressIndicator()),
              );

              try {
                final routine = {
                  'title': titleController.text,
                  'routine_date':
                      '${selectedDate.year}-${selectedDate.month.toString().padLeft(2, '0')}-${selectedDate.day.toString().padLeft(2, '0')}',
                  'routine_time':
                      '${selectedTime.hour.toString().padLeft(2, '0')}:${selectedTime.minute.toString().padLeft(2, '0')}',
                  'personality': personality,
                  'reminder_minutes_before': 10,
                  'grace_minutes_after': 5,
                };

                await ApiService.createRoutine(routine);

                if (mounted) Navigator.of(context).pop(); // close loader

                if (!mounted) return;

                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('✅ Routine created!'),
                    backgroundColor: AppColors.success,
                  ),
                );

                await _loadRoutines();

              } catch (e) {
                if (mounted) Navigator.of(context).pop();

                if (!mounted) return;

                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Error: $e'),
                    backgroundColor: AppColors.error,
                  ),
                );
              }
            },
            child: Text('Create'),
          ),
        ],
      ),
    ),
  );
}


  Future<void> _editRoutine(int index) async {
    final routine = _routines[index];
    final titleController = TextEditingController(text: routine['title']);
    
    final timeParts = routine['routine_time'].split(':');
    TimeOfDay selectedTime = TimeOfDay(
      hour: int.parse(timeParts[0]),
      minute: int.parse(timeParts[1]),
    );
    
    String personality = routine['personality'] ?? 'hood';

    await showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: Text('Edit Routine'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: titleController,
                  decoration: InputDecoration(
                    labelText: 'Routine Name',
                    border: OutlineInputBorder(),
                  ),
                ),
                SizedBox(height: 16),
                InkWell(
                  onTap: () async {
                    final time = await showTimePicker(
                      context: context,
                      initialTime: selectedTime,
                    );
                    if (time != null) {
                      setDialogState(() {
                        selectedTime = time;
                      });
                    }
                  },
                  child: InputDecorator(
                    decoration: InputDecoration(
                      labelText: 'Time',
                      border: OutlineInputBorder(),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(selectedTime.format(context)),
                        Icon(Icons.access_time),
                      ],
                    ),
                  ),
                ),
                SizedBox(height: 16),
                DropdownButtonFormField<String>(
                  value: personality,
                  decoration: InputDecoration(
                    labelText: 'AI Voice',
                    border: OutlineInputBorder(),
                  ),
                  items: [
                    DropdownMenuItem(value: 'hood', child: Text('🔥 Hood')),
                    DropdownMenuItem(value: 'calm', child: Text('😌 Calm')),
                    DropdownMenuItem(value: 'strict', child: Text('💪 Strict')),
                    DropdownMenuItem(value: 'motivational', child: Text('🏆 Motivational')),
                  ],
                  onChanged: (value) {
                    setDialogState(() {
                      personality = value!;
                    });
                  },
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                if (titleController.text.isEmpty) {
                  return;
                }

                Navigator.pop(context);
                
                setState(() {
                  _routines[index]['title'] = titleController.text;
                  _routines[index]['routine_time'] = 
                    '${selectedTime.hour.toString().padLeft(2, '0')}:${selectedTime.minute.toString().padLeft(2, '0')}';
                  _routines[index]['personality'] = personality;
                });
                
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('✅ Routine updated!'), backgroundColor: AppColors.success),
                );
                
                _loadRoutines();
              },
              child: Text('Save'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _deleteRoutine(int index) async {
  final routine = _routines[index];
  final routineId = routine['id'];
  
  // Remove from UI immediately
  setState(() {
    _routines.removeAt(index);
  });

  // Track if undone
  bool wasUndone = false;

  // Get scaffold messenger reference
  final messenger = ScaffoldMessenger.of(context);
  
  // Show snackbar
  messenger.showSnackBar(
    SnackBar(
      content: Text('Routine deleted'),
      backgroundColor: AppColors.error,
      duration: Duration(seconds: 4),
      behavior: SnackBarBehavior.floating,
      action: SnackBarAction(
        label: 'UNDO',
        textColor: AppColors.white,
        onPressed: () {
          wasUndone = true;
          
          // Clear the snackbar immediately
          messenger.clearSnackBars();
          
          // Restore routine
          setState(() {
            _routines.insert(index, routine);
          });
          
          // Show restored message
          messenger.showSnackBar(
            SnackBar(
              content: Text('✅ Routine restored'),
              backgroundColor: AppColors.success,
              duration: Duration(seconds: 2),
              behavior: SnackBarBehavior.floating,
            ),
          );
        },
      ),
    ),
  );

  // Wait 4 seconds
  await Future.delayed(Duration(seconds: 4));
  
  // Clear the snackbar after timeout
  if (!wasUndone && mounted) {
    messenger.clearSnackBars();
  }
  
  // Delete from backend if not undone
  if (!wasUndone && mounted) {
    try {
      await ApiService.deleteRoutine(routineId);
      print('✅ Deleted from backend');
    } catch (e) {
      print('❌ Error: $e');
      if (mounted) {
        setState(() {
          if (!_routines.any((r) => r['id'] == routineId)) {
            _routines.insert(index, routine);
          }
        });
        
        messenger.showSnackBar(
          SnackBar(
            content: Text('❌ Failed to delete'),
            backgroundColor: AppColors.error,
            duration: Duration(seconds: 2),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }
}

  Future<void> _completeRoutine(int id) async {
    try {
      await ApiService.completeRoutine(id);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('✅ Routine completed!'), backgroundColor: AppColors.success),
      );
      _loadRoutines();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e'), backgroundColor: AppColors.error),
      );
    }
  }
} // ← CLOSING BRACKET FOR _HomeScreenState CLASS

// Routine Card Widget
class _RoutineCard extends StatelessWidget {
  final Map<String, dynamic> routine;
  final VoidCallback onComplete;
  final VoidCallback onEdit;
  final VoidCallback onDelete;

  _RoutineCard({
    required this.routine,
    required this.onComplete,
    required this.onEdit,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    Color statusColor;
    IconData statusIcon;

    switch (routine['status']) {
      case 'done':
        statusColor = AppColors.success;
        statusIcon = Icons.check_circle_rounded;
        break;
      case 'missed':
        statusColor = AppColors.error;
        statusIcon = Icons.cancel_rounded;
        break;
      default:
        statusColor = AppColors.warning;
        statusIcon = Icons.pending_rounded;
    }

    return GestureDetector(
      onLongPress: () {
        showModalBottomSheet(
          context: context,
          builder: (context) => Container(
            padding: EdgeInsets.all(20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                ListTile(
                  leading: Icon(Icons.edit, color: AppColors.mediumBlue),
                  title: Text('Edit Routine'),
                  onTap: () {
                    Navigator.pop(context);
                    onEdit();
                  },
                ),
                ListTile(
                  leading: Icon(Icons.delete, color: AppColors.error),
                  title: Text('Delete Routine'),
                  onTap: () {
                    Navigator.pop(context);
                    onDelete();
                  },
                ),
                SizedBox(height: 10),
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: Text('Cancel'),
                ),
              ],
            ),
          ),
        );
      },
      child: Card(
        margin: EdgeInsets.only(bottom: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(color: statusColor, width: 2),
        ),
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Row(
            children: [
              Icon(statusIcon, size: 40, color: statusColor),
              SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(routine['title'], style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                    Text(routine['routine_time'], style: TextStyle(color: AppColors.gray)),
                    if (routine['streak'] != null && routine['streak'] > 0)
                      Text('🔥 ${routine['streak']} day streak', 
                           style: TextStyle(color: Color(0xFFF97316), fontWeight: FontWeight.bold)),
                  ],
                ),
              ),
              if (routine['status'] == 'pending')
                IconButton(
                  onPressed: onComplete,
                  icon: Icon(Icons.check, color: AppColors.white),
                  style: IconButton.styleFrom(backgroundColor: AppColors.success),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

// Stat Card Widget
class _StatCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;

  _StatCard({required this.title, required this.value, required this.icon, required this.color});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, color: color, size: 32),
            SizedBox(height: 8),
            Text(value, style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            Text(title, style: TextStyle(color: AppColors.gray)),
          ],
        ),
      ),
    );
  }
}