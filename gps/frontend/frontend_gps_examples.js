// GPS 定位功能前端範例程式碼
// 適用於 Web (JavaScript) 和 Flutter (Dart)

// ==================== JavaScript (Web) 版本 ====================

class LocationService {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }

    // 獲取用戶當前位置
    async getCurrentPosition() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('瀏覽器不支援定位功能'));
                return;
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    resolve({
                        latitude: position.coords.latitude,
                        longitude: position.coords.longitude,
                        accuracy: position.coords.accuracy
                    });
                },
                (error) => {
                    reject(new Error(`定位失敗: ${error.message}`));
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 300000 // 5 分鐘
                }
            );
        });
    }

    // 更新用戶定位到伺服器
    async updateUserLocation(userId, latitude, longitude) {
        try {
            const response = await fetch(`${this.baseURL}/users/${userId}/location`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    latitude: latitude,
                    longitude: longitude
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('更新定位失敗:', error);
            throw error;
        }
    }

    // 獲取用戶定位
    async getUserLocation(userId) {
        try {
            const response = await fetch(`${this.baseURL}/users/${userId}/location`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('獲取定位失敗:', error);
            throw error;
        }
    }

    // 查詢附近用戶
    async getNearbyUsers(userId, radiusKm = 5) {
        try {
            const response = await fetch(`${this.baseURL}/users/${userId}/nearby?radius_km=${radiusKm}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('查詢附近用戶失敗:', error);
            throw error;
        }
    }

    // 自動更新定位（定時）
    startLocationTracking(userId, intervalMinutes = 5) {
        return setInterval(async () => {
            try {
                const position = await this.getCurrentPosition();
                await this.updateUserLocation(userId, position.latitude, position.longitude);
                console.log('定位自動更新成功');
            } catch (error) {
                console.error('自動定位更新失敗:', error);
            }
        }, intervalMinutes * 60 * 1000);
    }

    // 停止定位追蹤
    stopLocationTracking(trackingId) {
        clearInterval(trackingId);
    }
}

// 使用範例
const locationService = new LocationService();

async function initLocationService() {
    const userId = 1; // 用戶 ID

    try {
        // 1. 獲取並更新當前位置
        console.log('正在獲取位置...');
        const position = await locationService.getCurrentPosition();
        console.log('位置獲取成功:', position);

        // 2. 上傳到伺服器
        const result = await locationService.updateUserLocation(
            userId, 
            position.latitude, 
            position.longitude
        );
        console.log('位置上傳成功:', result);

        // 3. 查詢附近用戶
        const nearbyUsers = await locationService.getNearbyUsers(userId, 10);
        console.log(`找到 ${nearbyUsers.length} 個附近用戶:`, nearbyUsers);

        // 4. 開始自動定位追蹤（每 5 分鐘更新一次）
        const trackingId = locationService.startLocationTracking(userId, 5);
        console.log('開始自動定位追蹤');

        // 可以在適當時機停止追蹤
        // locationService.stopLocationTracking(trackingId);

    } catch (error) {
        console.error('定位服務初始化失敗:', error);
        alert('定位功能無法使用: ' + error.message);
    }
}

// ==================== Flutter (Dart) 版本 ====================

/*
// 需要先安裝依賴套件
dependencies:
  geolocator: ^9.0.2
  http: ^0.13.5
  permission_handler: ^10.4.3

// 在 Android 的 android/app/src/main/AndroidManifest.xml 中添加權限：
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />

// 在 iOS 的 ios/Runner/Info.plist 中添加：
<key>NSLocationWhenInUseUsageDescription</key>
<string>此應用需要存取您的位置以提供附近用戶功能</string>
*/

/*
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'package:permission_handler/permission_handler.dart';
import 'dart:convert';
import 'dart:async';

class LocationService {
  final String baseURL;
  Timer? _locationTimer;

  LocationService({this.baseURL = 'http://localhost:8000'});

  // 檢查並請求定位權限
  Future<bool> checkLocationPermission() async {
    var status = await Permission.location.status;
    if (status.isDenied) {
      status = await Permission.location.request();
    }
    return status.isGranted;
  }

  // 獲取當前位置
  Future<Position> getCurrentPosition() async {
    bool hasPermission = await checkLocationPermission();
    if (!hasPermission) {
      throw Exception('定位權限被拒絕');
    }

    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw Exception('定位服務未啟用');
    }

    return await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.high,
    );
  }

  // 更新用戶定位到伺服器
  Future<Map<String, dynamic>> updateUserLocation(int userId, double latitude, double longitude) async {
    final response = await http.post(
      Uri.parse('$baseURL/users/$userId/location'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'latitude': latitude,
        'longitude': longitude,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('更新定位失敗: ${response.statusCode}');
    }
  }

  // 獲取用戶定位
  Future<Map<String, dynamic>> getUserLocation(int userId) async {
    final response = await http.get(
      Uri.parse('$baseURL/users/$userId/location'),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('獲取定位失敗: ${response.statusCode}');
    }
  }

  // 查詢附近用戶
  Future<List<dynamic>> getNearbyUsers(int userId, double radiusKm) async {
    final response = await http.get(
      Uri.parse('$baseURL/users/$userId/nearby?radius_km=$radiusKm'),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('查詢附近用戶失敗: ${response.statusCode}');
    }
  }

  // 開始定位追蹤
  void startLocationTracking(int userId, {int intervalMinutes = 5}) {
    _locationTimer = Timer.periodic(
      Duration(minutes: intervalMinutes),
      (timer) async {
        try {
          final position = await getCurrentPosition();
          await updateUserLocation(userId, position.latitude, position.longitude);
          print('定位自動更新成功');
        } catch (e) {
          print('自動定位更新失敗: $e');
        }
      },
    );
  }

  // 停止定位追蹤
  void stopLocationTracking() {
    _locationTimer?.cancel();
    _locationTimer = null;
  }
}

// 使用範例 Widget
class LocationWidget extends StatefulWidget {
  @override
  _LocationWidgetState createState() => _LocationWidgetState();
}

class _LocationWidgetState extends State<LocationWidget> {
  final LocationService _locationService = LocationService();
  final int userId = 1; // 用戶 ID
  String _statusText = '準備中...';
  List<dynamic> _nearbyUsers = [];

  @override
  void initState() {
    super.initState();
    _initLocationService();
  }

  Future<void> _initLocationService() async {
    try {
      setState(() => _statusText = '正在獲取位置...');
      
      final position = await _locationService.getCurrentPosition();
      setState(() => _statusText = '位置獲取成功: ${position.latitude}, ${position.longitude}');

      final result = await _locationService.updateUserLocation(
          userId, position.latitude, position.longitude);
      setState(() => _statusText = '位置上傳成功');

      final nearbyUsers = await _locationService.getNearbyUsers(userId, 10);
      setState(() {
        _nearbyUsers = nearbyUsers;
        _statusText = '找到 ${nearbyUsers.length} 個附近用戶';
      });

      _locationService.startLocationTracking(userId, intervalMinutes: 5);

    } catch (e) {
      setState(() => _statusText = '錯誤: $e');
    }
  }

  @override
  void dispose() {
    _locationService.stopLocationTracking();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('GPS 定位功能')),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('狀態: $_statusText'),
            SizedBox(height: 20),
            Text('附近用戶 (${_nearbyUsers.length} 個):'),
            Expanded(
              child: ListView.builder(
                itemCount: _nearbyUsers.length,
                itemBuilder: (context, index) {
                  final user = _nearbyUsers[index];
                  return ListTile(
                    title: Text(user['nickname'] ?? 'Unknown'),
                    subtitle: Text('ID: ${user['id']}'),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
*/
