import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

// Month Grid Screen - Shows 12 months
class MonthGridScreen extends StatelessWidget {
  final Function(DateTime) onMonthSelected;

  MonthGridScreen({required this.onMonthSelected});

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final months = List.generate(12, (index) {
      return DateTime(now.year, index + 1, 1);
    });

    return Scaffold(
      appBar: AppBar(
        title: Text('Select Month'),
        backgroundColor: AppColors.darkBlue,
      ),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: GridView.builder(
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 3,
            crossAxisSpacing: 16,
            mainAxisSpacing: 16,
            childAspectRatio: 1.2,
          ),
          itemCount: 12,
          itemBuilder: (context, index) {
            return _MonthCard(
              month: months[index],
              onTap: () => onMonthSelected(months[index]),
            );
          },
        ),
      ),
    );
  }
}

// Month Card Widget
class _MonthCard extends StatefulWidget {
  final DateTime month;
  final VoidCallback onTap;

  _MonthCard({required this.month, required this.onTap});

  @override
  _MonthCardState createState() => _MonthCardState();
}

class _MonthCardState extends State<_MonthCard> 
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(milliseconds: 200),
      vsync: this,
    );
    _scaleAnimation = Tween<double>(begin: 1.0, end: 0.95).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final monthName = DateFormat('MMMM').format(widget.month);
    final monthShort = DateFormat('MMM').format(widget.month);
    final now = DateTime.now();
    final isCurrentMonth = widget.month.month == now.month;

    // Different colors for seasons
    Color cardColor;
    if (widget.month.month >= 3 && widget.month.month <= 5) {
      cardColor = Color(0xFF10B981); // Spring - Green
    } else if (widget.month.month >= 6 && widget.month.month <= 8) {
      cardColor = Color(0xFFF59E0B); // Summer - Yellow
    } else if (widget.month.month >= 9 && widget.month.month <= 11) {
      cardColor = Color(0xFFF97316); // Fall - Orange
    } else {
      cardColor = Color(0xFF3B82F6); // Winter - Blue
    }

    return ScaleTransition(
      scale: _scaleAnimation,
      child: GestureDetector(
        onTapDown: (_) => _controller.forward(),
        onTapUp: (_) {
          _controller.reverse();
          widget.onTap();
        },
        onTapCancel: () => _controller.reverse(),
        child: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                cardColor,
                cardColor.withOpacity(0.7),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: cardColor.withOpacity(0.3),
                blurRadius: 8,
                offset: Offset(0, 4),
              ),
            ],
            border: isCurrentMonth
                ? Border.all(color: Colors.white, width: 3)
                : null,
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                monthShort.toUpperCase(),
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 2,
                ),
              ),
              if (isCurrentMonth)
                Container(
                  margin: EdgeInsets.only(top: 4),
                  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    'NOW',
                    style: TextStyle(
                      color: cardColor,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

// Full Month Calendar View
class MonthCalendarView extends StatefulWidget {
  final DateTime initialMonth;
  final List<Map<String, dynamic>> routines;
  final Function(DateTime) onDaySelected;

  MonthCalendarView({
    required this.initialMonth,
    required this.routines,
    required this.onDaySelected,
  });

  @override
  _MonthCalendarViewState createState() => _MonthCalendarViewState();
}

class _MonthCalendarViewState extends State<MonthCalendarView> {
  late DateTime _currentMonth;
  late PageController _pageController;

  @override
  void initState() {
    super.initState();
    _currentMonth = widget.initialMonth;
    _pageController = PageController(initialPage: 1000);
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  void _previousMonth() {
    _pageController.previousPage(
      duration: Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  void _nextMonth() {
    _pageController.nextPage(
      duration: Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(DateFormat('MMMM yyyy').format(_currentMonth)),
        backgroundColor: AppColors.darkBlue,
        actions: [
          IconButton(
            icon: Icon(Icons.today),
            onPressed: () {
              setState(() {
                _currentMonth = DateTime.now();
              });
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Month navigation
          Container(
            padding: EdgeInsets.symmetric(vertical: 16),
            color: AppColors.veryLightBlue,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                IconButton(
                  icon: Icon(Icons.chevron_left, size: 32),
                  onPressed: _previousMonth,
                  color: AppColors.darkBlue,
                ),
                Text(
                  DateFormat('MMMM yyyy').format(_currentMonth),
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: AppColors.darkBlue,
                  ),
                ),
                IconButton(
                  icon: Icon(Icons.chevron_right, size: 32),
                  onPressed: _nextMonth,
                  color: AppColors.darkBlue,
                ),
              ],
            ),
          ),

          // Weekday headers
          Container(
            padding: EdgeInsets.symmetric(vertical: 8),
            color: AppColors.mediumBlue,
            child: Row(
              children: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
                  .map((day) => Expanded(
                        child: Center(
                          child: Text(
                            day,
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ))
                  .toList(),
            ),
          ),

          // Calendar grid
          Expanded(
            child: PageView.builder(
              controller: _pageController,
              onPageChanged: (index) {
                setState(() {
                  final offset = index - 1000;
                  _currentMonth = DateTime(
                    widget.initialMonth.year,
                    widget.initialMonth.month + offset,
                    1,
                  );
                });
              },
              itemBuilder: (context, index) {
                final offset = index - 1000;
                final month = DateTime(
                  widget.initialMonth.year,
                  widget.initialMonth.month + offset,
                  1,
                );
                return _buildCalendarGrid(month);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCalendarGrid(DateTime month) {
    final daysInMonth = DateUtils.getDaysInMonth(month.year, month.month);
    final firstDayOfMonth = DateTime(month.year, month.month, 1);
    final firstWeekday = firstDayOfMonth.weekday % 7; // 0 = Sunday

    final days = <Widget>[];

    // Empty cells before first day
    for (int i = 0; i < firstWeekday; i++) {
      days.add(Container());
    }

    // Days of month
    for (int day = 1; day <= daysInMonth; day++) {
      final date = DateTime(month.year, month.month, day);
      days.add(_DayCell(
        date: date,
        routines: widget.routines,
        onTap: () => widget.onDaySelected(date),
      ));
    }

    return GridView.count(
      crossAxisCount: 7,
      padding: EdgeInsets.all(8),
      children: days,
    );
  }
}

// Day Cell Widget
class _DayCell extends StatefulWidget {
  final DateTime date;
  final List<Map<String, dynamic>> routines;
  final VoidCallback onTap;

  _DayCell({
    required this.date,
    required this.routines,
    required this.onTap,
  });

  @override
  _DayCellState createState() => _DayCellState();
}

class _DayCellState extends State<_DayCell> 
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(milliseconds: 150),
      vsync: this,
    );
    _scaleAnimation = Tween<double>(begin: 1.0, end: 0.9).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final now = DateTime.now();
    final isToday = widget.date.year == now.year &&
        widget.date.month == now.month &&
        widget.date.day == now.day;

    final isPast = widget.date.isBefore(
      DateTime(now.year, now.month, now.day),
    );

    // Check if there are routines on this day
    final dayRoutines = widget.routines.where((r) {
      final routineDate = DateTime.parse(r['routine_date']);
      return routineDate.year == widget.date.year &&
          routineDate.month == widget.date.month &&
          routineDate.day == widget.date.day;
    }).toList();

    final hasRoutines = dayRoutines.isNotEmpty;
    final completedCount = dayRoutines.where((r) => r['status'] == 'done').length;
    final allCompleted = hasRoutines && completedCount == dayRoutines.length;

    return ScaleTransition(
      scale: _scaleAnimation,
      child: GestureDetector(
        onTapDown: (_) => _controller.forward(),
        onTapUp: (_) {
          _controller.reverse();
          widget.onTap();
        },
        onTapCancel: () => _controller.reverse(),
        child: Container(
          margin: EdgeInsets.all(4),
          decoration: BoxDecoration(
            color: isToday
                ? AppColors.mediumBlue
                : allCompleted
                    ? AppColors.success.withOpacity(0.2)
                    : hasRoutines
                        ? AppColors.warning.withOpacity(0.2)
                        : isPast
                            ? AppColors.gray.withOpacity(0.1)
                            : Colors.white,
            borderRadius: BorderRadius.circular(8),
            border: isToday
                ? Border.all(color: AppColors.white, width: 2)
                : hasRoutines
                    ? Border.all(
                        color: allCompleted
                            ? AppColors.success
                            : AppColors.warning,
                        width: 2,
                      )
                    : null,
            boxShadow: isToday
                ? [
                    BoxShadow(
                      color: AppColors.mediumBlue.withOpacity(0.3),
                      blurRadius: 8,
                      offset: Offset(0, 2),
                    ),
                  ]
                : null,
          ),
          child: Stack(
            children: [
              Center(
                child: Text(
                  '${widget.date.day}',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: isToday ? FontWeight.bold : FontWeight.normal,
                    color: isToday
                        ? Colors.white
                        : isPast
                            ? AppColors.gray
                            : AppColors.darkBlue,
                  ),
                ),
              ),
              if (hasRoutines)
                Positioned(
                  bottom: 2,
                  left: 0,
                  right: 0,
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: List.generate(
                      dayRoutines.length > 3 ? 3 : dayRoutines.length,
                      (index) => Container(
                        width: 4,
                        height: 4,
                        margin: EdgeInsets.symmetric(horizontal: 1),
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: dayRoutines[index]['status'] == 'done'
                              ? AppColors.success
                              : AppColors.warning,
                        ),
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

// AppColors class (add if not already in your code)
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