import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';

class EnhancedStatsScreen extends StatefulWidget {
  final List<Map<String, dynamic>> routines;

  EnhancedStatsScreen({required this.routines});

  @override
  _EnhancedStatsScreenState createState() => _EnhancedStatsScreenState();
}

class _EnhancedStatsScreenState extends State<EnhancedStatsScreen> {
  int _selectedPeriod = 7; // 7 or 30 days

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: Text('Statistics'),
          backgroundColor: AppColors.darkBlue,
          bottom: TabBar(
            indicatorColor: AppColors.white,
            labelColor: AppColors.white,
            unselectedLabelColor: AppColors.white.withOpacity(0.6),
            tabs: [
              Tab(text: 'Overview'),
              Tab(text: 'Charts'),
              Tab(text: 'Records'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _buildOverviewTab(),
            _buildChartsTab(),
            _buildRecordsTab(),
          ],
        ),
      ),
    );
  }

  // Overview Tab
  Widget _buildOverviewTab() {
    final total = widget.routines.length;
    final completed = widget.routines.where((r) => r['status'] == 'done').length;
    final missed = widget.routines.where((r) => r['status'] == 'missed').length;
    final pending = widget.routines.where((r) => r['status'] == 'pending').length;
    
    final completionRate = total > 0 ? ((completed / total) * 100).toStringAsFixed(0) : '0';
    
    // Calculate current streak
    final currentStreak = _calculateCurrentStreak();
    final bestStreak = _calculateBestStreak();

    return SingleChildScrollView(
      padding: EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Hero Card - Completion Rate
          Container(
            width: double.infinity,
            padding: EdgeInsets.all(24),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [AppColors.darkBlue, AppColors.mediumBlue],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: AppColors.mediumBlue.withOpacity(0.3),
                  blurRadius: 10,
                  offset: Offset(0, 4),
                ),
              ],
            ),
            child: Column(
              children: [
                Text(
                  'Overall Completion Rate',
                  style: TextStyle(
                    color: AppColors.white.withOpacity(0.9),
                    fontSize: 16,
                  ),
                ),
                SizedBox(height: 12),
                Text(
                  '$completionRate%',
                  style: TextStyle(
                    color: AppColors.white,
                    fontSize: 56,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  '$completed of $total routines completed',
                  style: TextStyle(
                    color: AppColors.white.withOpacity(0.8),
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),

          SizedBox(height: 24),

          // Streak Cards
          Row(
            children: [
              Expanded(
                child: _buildStreakCard(
                  '🔥 Current Streak',
                  '$currentStreak days',
                  Color(0xFFF97316),
                ),
              ),
              SizedBox(width: 16),
              Expanded(
                child: _buildStreakCard(
                  '🏆 Best Streak',
                  '$bestStreak days',
                  Color(0xFFFBBF24),
                ),
              ),
            ],
          ),

          SizedBox(height: 24),

          // Stats Grid
          Text(
            'Quick Stats',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: AppColors.darkBlue,
            ),
          ),
          SizedBox(height: 16),

          Row(
            children: [
              Expanded(
                child: _StatCard(
                  title: 'Total',
                  value: '$total',
                  icon: Icons.list_rounded,
                  color: AppColors.mediumBlue,
                ),
              ),
              SizedBox(width: 16),
              Expanded(
                child: _StatCard(
                  title: 'Done',
                  value: '$completed',
                  icon: Icons.check_circle_rounded,
                  color: AppColors.success,
                ),
              ),
            ],
          ),
          SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _StatCard(
                  title: 'Pending',
                  value: '$pending',
                  icon: Icons.pending_rounded,
                  color: AppColors.warning,
                ),
              ),
              SizedBox(width: 16),
              Expanded(
                child: _StatCard(
                  title: 'Missed',
                  value: '$missed',
                  icon: Icons.cancel_rounded,
                  color: AppColors.error,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // Charts Tab
  Widget _buildChartsTab() {
    return SingleChildScrollView(
      padding: EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Period Selector
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _PeriodButton(
                label: 'Last 7 Days',
                isSelected: _selectedPeriod == 7,
                onTap: () => setState(() => _selectedPeriod = 7),
              ),
              SizedBox(width: 12),
              _PeriodButton(
                label: 'Last 30 Days',
                isSelected: _selectedPeriod == 30,
                onTap: () => setState(() => _selectedPeriod = 30),
              ),
            ],
          ),

          SizedBox(height: 24),

          // Completion Trend Chart
          Text(
            'Completion Trend',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppColors.darkBlue,
            ),
          ),
          SizedBox(height: 16),
          _buildCompletionTrendChart(),

          SizedBox(height: 32),

          // Day of Week Chart
          Text(
            'Routines by Day of Week',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppColors.darkBlue,
            ),
          ),
          SizedBox(height: 16),
          _buildDayOfWeekChart(),

          SizedBox(height: 32),

          // Status Distribution
          Text(
            'Status Distribution',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: AppColors.darkBlue,
            ),
          ),
          SizedBox(height: 16),
          _buildStatusPieChart(),
        ],
      ),
    );
  }

  // Records Tab
  Widget _buildRecordsTab() {
    final records = _calculateRecords();

    return ListView(
      padding: EdgeInsets.all(16),
      children: [
        _RecordCard(
          icon: Icons.whatshot,
          title: 'Longest Streak',
          value: '${records['longestStreak']} days',
          subtitle: 'Your personal best!',
          color: Color(0xFFF97316),
        ),
        SizedBox(height: 12),
        _RecordCard(
          icon: Icons.check_circle,
          title: 'Total Completed',
          value: '${records['totalCompleted']}',
          subtitle: 'All-time completions',
          color: AppColors.success,
        ),
        SizedBox(height: 12),
        _RecordCard(
          icon: Icons.calendar_today,
          title: 'Most Productive Day',
          value: records['mostProductiveDay'],
          subtitle: 'Day with most completions',
          color: AppColors.mediumBlue,
        ),
        SizedBox(height: 12),
        _RecordCard(
          icon: Icons.access_time,
          title: 'Best Time of Day',
          value: records['bestTimeOfDay'],
          subtitle: 'When you complete most',
          color: AppColors.warning,
        ),
        SizedBox(height: 12),
        _RecordCard(
          icon: Icons.star,
          title: 'Success Rate',
          value: '${records['successRate']}%',
          subtitle: 'Overall completion rate',
          color: Color(0xFFFBBF24),
        ),
      ],
    );
  }

  // Build Streak Card
  Widget _buildStreakCard(String title, String value, Color color) {
    return Container(
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color, width: 2),
      ),
      child: Column(
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 14,
              color: AppColors.darkBlue,
            ),
            textAlign: TextAlign.center,
          ),
          SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  // Build Completion Trend Chart
  Widget _buildCompletionTrendChart() {
    final data = _getCompletionTrendData();

    return Container(
      height: 200,
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: AppColors.gray.withOpacity(0.1),
            blurRadius: 10,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: LineChart(
        LineChartData(
          gridData: FlGridData(show: false),
          titlesData: FlTitlesData(
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 40,
                getTitlesWidget: (value, meta) {
                  return Text(
                    value.toInt().toString(),
                    style: TextStyle(fontSize: 12),
                  );
                },
              ),
            ),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                getTitlesWidget: (value, meta) {
                  if (value.toInt() >= 0 && value.toInt() < data.length) {
                    return Padding(
                      padding: EdgeInsets.only(top: 8),
                      child: Text(
                        data[value.toInt()]['label'],
                        style: TextStyle(fontSize: 10),
                      ),
                    );
                  }
                  return Text('');
                },
              ),
            ),
            rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          borderData: FlBorderData(show: false),
          lineBarsData: [
            LineChartBarData(
              spots: data.asMap().entries.map((e) {
                return FlSpot(e.key.toDouble(), e.value['completed'].toDouble());
              }).toList(),
              isCurved: true,
              color: AppColors.success,
              barWidth: 3,
              dotData: FlDotData(show: true),
              belowBarData: BarAreaData(
                show: true,
                color: AppColors.success.withOpacity(0.1),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // Build Day of Week Chart
  Widget _buildDayOfWeekChart() {
    final dayData = _getDayOfWeekData();

    return Container(
      height: 200,
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: AppColors.gray.withOpacity(0.1),
            blurRadius: 10,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: BarChart(
        BarChartData(
          alignment: BarChartAlignment.spaceAround,
          gridData: FlGridData(show: false),
          titlesData: FlTitlesData(
            leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                getTitlesWidget: (value, meta) {
                  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
                  if (value.toInt() >= 0 && value.toInt() < days.length) {
                    return Padding(
                      padding: EdgeInsets.only(top: 8),
                      child: Text(days[value.toInt()], style: TextStyle(fontSize: 12)),
                    );
                  }
                  return Text('');
                },
              ),
            ),
          ),
          borderData: FlBorderData(show: false),
          barGroups: dayData.asMap().entries.map((e) {
            return BarChartGroupData(
              x: e.key,
              barRods: [
                BarChartRodData(
                  toY: e.value.toDouble(),
                  color: AppColors.mediumBlue,
                  width: 20,
                  borderRadius: BorderRadius.circular(4),
                ),
              ],
            );
          }).toList(),
        ),
      ),
    );
  }

  // Build Status Pie Chart
  Widget _buildStatusPieChart() {
    final completed = widget.routines.where((r) => r['status'] == 'done').length;
    final missed = widget.routines.where((r) => r['status'] == 'missed').length;
    final pending = widget.routines.where((r) => r['status'] == 'pending').length;
    final total = completed + missed + pending;

    if (total == 0) {
      return Container(
        height: 200,
        child: Center(child: Text('No data yet')),
      );
    }

    return Container(
      height: 200,
      padding: EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: AppColors.gray.withOpacity(0.1),
            blurRadius: 10,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            flex: 2,
            child: PieChart(
              PieChartData(
                sectionsSpace: 2,
                centerSpaceRadius: 40,
                sections: [
                  PieChartSectionData(
                    value: completed.toDouble(),
                    title: '$completed',
                    color: AppColors.success,
                    radius: 50,
                    titleStyle: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: AppColors.white,
                    ),
                  ),
                  PieChartSectionData(
                    value: missed.toDouble(),
                    title: '$missed',
                    color: AppColors.error,
                    radius: 50,
                    titleStyle: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: AppColors.white,
                    ),
                  ),
                  PieChartSectionData(
                    value: pending.toDouble(),
                    title: '$pending',
                    color: AppColors.warning,
                    radius: 50,
                    titleStyle: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: AppColors.white,
                    ),
                  ),
                ],
              ),
            ),
          ),
          SizedBox(width: 16),
          Expanded(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _LegendItem('Done', AppColors.success),
                SizedBox(height: 8),
                _LegendItem('Missed', AppColors.error),
                SizedBox(height: 8),
                _LegendItem('Pending', AppColors.warning),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // Data Calculations
  List<Map<String, dynamic>> _getCompletionTrendData() {
    final now = DateTime.now();
    final data = <Map<String, dynamic>>[];

    for (int i = _selectedPeriod - 1; i >= 0; i--) {
      final date = now.subtract(Duration(days: i));
      final dateStr = DateFormat('yyyy-MM-dd').format(date);
      
      final dayRoutines = widget.routines.where((r) {
        return r['routine_date'] == dateStr;
      }).toList();
      
      final completed = dayRoutines.where((r) => r['status'] == 'done').length;
      
      data.add({
        'label': i == 0 ? 'Today' : DateFormat('M/d').format(date),
        'completed': completed,
      });
    }

    return data;
  }

  List<int> _getDayOfWeekData() {
    final counts = List<int>.filled(7, 0);
    
    for (var routine in widget.routines) {
      if (routine['status'] == 'done') {
        final date = DateTime.parse(routine['routine_date']);
        final weekday = date.weekday; // 1 = Monday, 7 = Sunday
        counts[weekday - 1]++;
      }
    }
    
    return counts;
  }

  int _calculateCurrentStreak() {
    if (widget.routines.isEmpty) return 0;
    
    final now = DateTime.now();
    int streak = 0;
    
    for (int i = 0; i < 365; i++) {
      final date = now.subtract(Duration(days: i));
      final dateStr = DateFormat('yyyy-MM-dd').format(date);
      
      final dayRoutines = widget.routines.where((r) => r['routine_date'] == dateStr).toList();
      
      if (dayRoutines.isEmpty) continue;
      
      final hasCompleted = dayRoutines.any((r) => r['status'] == 'done');
      
      if (hasCompleted) {
        streak++;
      } else {
        break;
      }
    }
    
    return streak;
  }

  int _calculateBestStreak() {
    if (widget.routines.isEmpty) return 0;
    
    int bestStreak = 0;
    int currentStreak = 0;
    
    final sortedDates = widget.routines
        .map((r) => DateTime.parse(r['routine_date']))
        .toSet()
        .toList()
      ..sort();
    
    for (var date in sortedDates) {
      final dateStr = DateFormat('yyyy-MM-dd').format(date);
      final dayRoutines = widget.routines.where((r) => r['routine_date'] == dateStr).toList();
      final hasCompleted = dayRoutines.any((r) => r['status'] == 'done');
      
      if (hasCompleted) {
        currentStreak++;
        bestStreak = currentStreak > bestStreak ? currentStreak : bestStreak;
      } else {
        currentStreak = 0;
      }
    }
    
    return bestStreak;
  }

  Map<String, dynamic> _calculateRecords() {
    final completed = widget.routines.where((r) => r['status'] == 'done').toList();
    
    // Most productive day
    final dayCounts = <String, int>{};
    for (var routine in completed) {
      final date = DateTime.parse(routine['routine_date']);
      final day = DateFormat('EEEE').format(date);
      dayCounts[day] = (dayCounts[day] ?? 0) + 1;
    }
    
    final mostProductiveDay = dayCounts.entries.isEmpty
        ? 'N/A'
        : dayCounts.entries.reduce((a, b) => a.value > b.value ? a : b).key;
    
    // Best time of day
    final hourCounts = <int, int>{};
    for (var routine in completed) {
      if (routine['routine_time'] != null) {
        final hour = int.parse(routine['routine_time'].split(':')[0]);
        hourCounts[hour] = (hourCounts[hour] ?? 0) + 1;
      }
    }
    
    String bestTimeOfDay = 'N/A';
    if (hourCounts.isNotEmpty) {
      final bestHour = hourCounts.entries.reduce((a, b) => a.value > b.value ? a : b).key;
      if (bestHour < 12) {
        bestTimeOfDay = '${bestHour}:00 AM';
      } else if (bestHour == 12) {
        bestTimeOfDay = '12:00 PM';
      } else {
        bestTimeOfDay = '${bestHour - 12}:00 PM';
      }
    }
    
    final total = widget.routines.length;
    final successRate = total > 0 ? ((completed.length / total) * 100).toStringAsFixed(0) : '0';
    
    return {
      'longestStreak': _calculateBestStreak(),
      'totalCompleted': completed.length,
      'mostProductiveDay': mostProductiveDay,
      'bestTimeOfDay': bestTimeOfDay,
      'successRate': successRate,
    };
  }
}

// Helper Widgets
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

class _PeriodButton extends StatelessWidget {
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  _PeriodButton({required this.label, required this.isSelected, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: EdgeInsets.symmetric(horizontal: 20, vertical: 10),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.darkBlue : AppColors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: AppColors.darkBlue, width: 2),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: isSelected ? AppColors.white : AppColors.darkBlue,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
}

class _LegendItem extends StatelessWidget {
  final String label;
  final Color color;

  _LegendItem(this.label, this.color);

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 16,
          height: 16,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        SizedBox(width: 8),
        Text(label, style: TextStyle(fontSize: 14)),
      ],
    );
  }
}

class _RecordCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String value;
  final String subtitle;
  final Color color;

  _RecordCard({
    required this.icon,
    required this.title,
    required this.value,
    required this.subtitle,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: Container(
          padding: EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: color, size: 24),
        ),
        title: Text(title, style: TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text(subtitle, style: TextStyle(fontSize: 12)),
        trailing: Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ),
    );
  }
}

// AppColors class (if not already in your code)
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