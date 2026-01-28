import 'package:device_info_plus/device_info_plus.dart';
import 'dart:io';

class UserService {
  static String? _deviceId;
  
  static Future<String> getDeviceId() async {
    if (_deviceId != null) return _deviceId!;
    
    try {
      DeviceInfoPlugin deviceInfo = DeviceInfoPlugin();
      
      if (Platform.isAndroid) {
        AndroidDeviceInfo androidInfo = await deviceInfo.androidInfo;
        _deviceId = androidInfo.id; // Unique Android ID
      } else if (Platform.isIOS) {
        IosDeviceInfo iosInfo = await deviceInfo.iosInfo;
        _deviceId = iosInfo.identifierForVendor; // Unique iOS ID
      } else {
        _deviceId = 'desktop_user';
      }
      
      print('📱 Device ID: $_deviceId');
      return _deviceId!;
    } catch (e) {
      print('Error getting device ID: $e');
      _deviceId = 'unknown_device';
      return _deviceId!;
    }
  }
}