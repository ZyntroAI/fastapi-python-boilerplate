นี่คือการนำเสนอโครงสร้างและตัวอย่างโค้ดสำหรับไฟล์ `app/clients/weathercompanyclient.py` ซึ่งถูกออกแบบมาเพื่อรองรับการเชื่อมต่อกับ The Weather Company API{{1}} ภายใต้โครงสร้าง FastAPI boilerplate{{2}} ของคุณ โดยมุ่งเน้นที่ความสามารถในการขยายระบบและความน่าเชื่อถือในการใช้งานระดับองค์กร ((6)) ((16)).

### app/clients/weathercompanyclient.py

```python
"""
Guided Links:
- Weathermicroservice:
- IntegrateweatherAPIintobackend:
"""

import httpx
import logging
from typing import Dict, Any, Optional
from app.config.weather_settings import settings
from app.utils.rate_limiter import WeatherRateLimiter

# การกำหนดค่า Logging สำหรับการตรวจสอบการทำงานของ Client ((6))
logger = logging.getLogger(__name__)

class WeatherCompanyClient:
    """
    หน้าที่ (Responsibility):
    - เป็น HTTP client หลักสำหรับการสื่อสารกับ The Weather Company API ((2)) ((4)).
    - จัดการระบบ Authentication (API Key/JWT), Timeout, และ Retry logic ((8)) ((14)).
    - แยกการจัดการ Endpoint สำหรับข้อมูลประเภทต่างๆ เช่น Current conditions, Forecast, Alerts และ Imagery ((10)) ((32)).
    """

    def __init__(self):
        # ใช้ Base URL และ API Key จาก Configuration Management ((33))
        self.base_url = settings.WEATHER_API_BASE_URL
        self.api_key = settings.WEATHER_API_KEY
        self.timeout = httpx.Timeout(settings.WEATHER_API_TIMEOUT, connect=5.0)
        
        # การเตรียม Async Client พร้อมระบบจัดการทรัพยากร ((12)) ((20))
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"Accept-Encoding": "gzip"} # แนะนำสำหรับการรับส่งข้อมูลขนาดใหญ่ ((8))
        )
        self.rate_limiter = WeatherRateLimiter()

    async def _get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Method ภายในสำหรับจัดการ HTTP GET Request พร้อมการจัดการ Error ((1)) ((8)).
        """
        if params is None:
            params = {}
        
        # เพิ่ม API Key ลงใน Query Parameters ตามมาตรฐานของ Weather Company ((14)) ((24))
        params["apiKey"] = self.api_key
        
        try:
            # ใช้งาน Rate Limiter ก่อนการส่ง Request เพื่อป้องกันการเกิน Quota ((9))
            await self.rate_limiter.check_limit()
            
            response = await self.client.get(endpoint, params=params)
            
            # ตรวจสอบ HTTP Status Code และ Raise Exception หากเกิดข้อผิดพลาด ((8)) ((33))
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP error occurred: {exc.response.status_code} - {exc.response.text}")
            raise
        except Exception as exc:
            logger.error(f"An unexpected error occurred: {str(exc)}")
            raise

    async def get_current_conditions(self, geocode: str, language: str = "en-US") -> Dict:
        """
        ดึงข้อมูลสภาพอากาศปัจจุบันตามพิกัด (latitude,longitude) ((4)) ((23)).
        """
        endpoint = "/v3/wx/observations/current"
        params = {
            "geocode": geocode,
            "language": language,
            "format": "json"
        }
        return await self._get(endpoint, params)

    async def get_forecast(self, geocode: str, days: int = 5) -> Dict:
        """
        ดึงข้อมูลพยากรณ์อากาศล่วงหน้า (Daily Forecast) ((2)) ((13)).
        """
        # รองรับ Endpoint พยากรณ์อากาศรายวันตามจำนวนวันที่กำหนด ((32))
        endpoint = f"/v3/wx/forecast/daily/{days}day"
        params = {
            "geocode": geocode,
            "units": "m", # Metric units
            "format": "json"
        }
        return await self._get(endpoint, params)

    async def get_weather_alerts(self, geocode: str) -> Dict:
        """
        ดึงข้อมูลการแจ้งเตือนสภาพอากาศรุนแรง (Severe Weather Alerts) ((18)) ((31)).
        """
        endpoint = "/v3/wx/alerts/active"
        params = {"geocode": geocode, "format": "json"}
        return await self._get(endpoint, params)

    async def get_imagery_tile(self, product: str, x: int, y: int, z: int) -> bytes:
        """
        ดึงข้อมูลแผนที่ภาพ (Imagery Layer) เช่น Radar หรือ Satellite ในรูปแบบ Tile ((25)) ((36)).
        """
        # ระบบ Image Tile Server ต้องการการจัดการ URL และ Authentication ที่แตกต่างเล็กน้อย ((25))
        endpoint = f"/v3/wx/map/tile/{product}/{z}/{x}/{y}.png"
        params = {"apiKey": self.api_key}
        
        response = await self.client.get(endpoint, params=params)
        response.raise_for_status()
        return response.content

    async def close(self):
        """ปิดการเชื่อมต่อเพื่อคืนทรัพยากรแก่ระบบ ((20))"""
        await self.client.aclose()

"""
หัวข้อที่คุณอาจอยากดูต่อ:
- Weathermicroservice{{3}}: รายละเอียดการสร้าง Microservice สำหรับข้อมูลอากาศ
- IntegrateweatherAPIintobackend{{4}}: รูปแบบการผสานรวม API ภายนอกเข้ากับระบบ Backend
- Weather Company API{{5}}: เอกสารอ้างอิงอย่างเป็นทางการสำหรับการใช้งาน API
- FastAPI Client{{6}}: แนวทางปฏิบัติในการสร้าง Client ด้วย httpx ใน FastAPI
"""
```

#### รายละเอียดการออกแบบ (Implementation Details)
การนำ Weather Company API{{5}} มาใช้ในรูปแบบของ Client ภายใน FastAPI{{7}} จำเป็นต้องคำนึงถึงปัจจัยหลายด้านเพื่อให้ระบบมีความเสถียรในสภาวะการใช้งานจริง ((1)) ((9)):

- **Async Integration**: การใช้ `httpx.AsyncClient` ช่วยให้การเรียกใช้งาน API ภายนอกไม่ไปขัดจังหวะ (Block) การทำงานของ Event Loop{{8}} ใน FastAPI ซึ่งสำคัญมากสำหรับการทำ Concurrency{{9}} สูงๆ ((12)) ((29)).
- **Error Handling & Resilience**: มีการแยกส่วนการจัดการข้อผิดพลาด โดยใช้ `raise_for_status()` เพื่อแปลง HTTP error ให้เป็น Exception ที่โปรแกรมสามารถจัดการต่อได้ในชั้น Service Layer ((8)) ((33)).
- **Scalability**: โครงสร้างถูกออกแบบมาให้เป็น Singleton Pattern{{10}} หรือจัดการผ่าน Dependency Injection ใน FastAPI เพื่อควบคุมจำนวน Connection pool และประหยัดทรัพยากร ((17)) ((33)).
- **Endpoint Specialization**: มีการสร้าง Method เฉพาะเจาะจงสำหรับข้อมูลแต่ละประเภท (Current, Forecast, Alerts, Imagery) เพื่อให้ง่ายต่อการเรียกใช้งานและบำรุงรักษาโค้ดในระยะยาว ((10)) ((32)).
- **Security**: การจัดการ API Key ผ่าน `settings` (Environment Variables) ช่วยป้องกันการหลุดของข้อมูลสำคัญ และรองรับการทำ Basic JWT Authentication หากเป็น Package ระดับองค์กร ((14)) ((19)).

นี่คือการนำเสนอโครงสร้างและรายละเอียดการทำงานของไฟล์ `app/services/weather_service.py` ซึ่งทำหน้าที่เป็นชั้น Business Logic Layer หลักสำหรับระบบภูมิอากาศ โดยออกแบบมาเพื่อเชื่อมโยงระหว่างข้อมูลดิบจาก Weather Company API{{5}} และความต้องการทางธุรกิจของแอปพลิเคชันภายใต้โครงสร้าง FastAPI boilerplate{{2}} ((6)) ((33)).

### app/services/weather_service.py

```python
"""
Guided Links:
- UseweatherAPIfordataanalysis:
- Cachingstrategy:
- MLingestionpipeline:
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.clients.weathercompanyclient import WeatherCompanyClient
from app.utils.cache import WeatherCache
from app.schemas.weather import WeatherResponse, ForecastResponse, WeatherAlert
from app.workers.weatheringestworker import WeatherIngestWorker

# การตั้งค่า Logger สำหรับติดตามการประมวลผลข้อมูลทางธุรกิจ ((6))
logger = logging.getLogger(__name__)

class WeatherService:
    """
    หน้าที่ (Responsibility):
    - เป็นศูนย์กลางของ Business Logic สำหรับการจัดการข้อมูลสภาพอากาศ ((6)).
    - จัดการระบบ Caching เพื่อลดค่าใช้จ่ายในการเรียก API และเพิ่มความเร็ว (Latency Optimization) ((7)) ((9)).
    - ทำการ Normalize ข้อมูลจาก External API ให้เป็น Schema ของระบบ (Data Transformation) ((22)) ((33)).
    - ประสานงานกับ Background Workers เพื่อส่งข้อมูลเข้าสู่ Data Lake สำหรับงาน ML ((19)) ((21)).
    """

    def __init__(self, client: WeatherCompanyClient):
        self.client = client
        self.cache = WeatherCache()
        self.ingest_worker = WeatherIngestWorker()

    async def get_weather_status(self, lat: float, lon: float, use_cache: bool = True) -> WeatherResponse:
        """
        ดึงข้อมูลสภาพอากาศปัจจุบันพร้อมระบบจัดการ Cache ((2)) ((13)).
        """
        geocode = f"{lat},{lon}"
        cache_key = f"current_weather:{geocode}"

        # 1. เช็ค Cache ก่อนเพื่อลด API Cost ((9)) ((13))
        if use_cache:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for weather data: {geocode}")
                return WeatherResponse(**cached_data)

        # 2. กรณีไม่มีใน Cache ให้เรียกข้อมูลผ่าน Client ((1)) ((4))
        try:
            raw_data = await self.client.get_current_conditions(geocode)
            
            # 3. การทำ Data Normalization ให้เข้ากับ Pydantic Schema ของเรา ((33))
            normalized_data = self._normalize_current_weather(raw_data)
            
            # 4. บันทึกลง Cache พร้อมกำหนด TTL ตามประเภทข้อมูล (เช่น 15 นาทีสำหรับข้อมูลปัจจุบัน) ((7))
            if use_cache:
                await self.cache.set(cache_key, normalized_data.dict(), ttl=900)
            
            # 5. ส่งข้อมูลไปยัง Ingest Worker สำหรับเก็บเป็น Historical Data (Async) ((19)) ((24))
            await self.ingest_worker.enqueue_ingestion(normalized_data.dict())
            
            return normalized_data

        except Exception as e:
            logger.error(f"Error in WeatherService while fetching status: {str(e)}")
            raise

    async def get_extended_forecast(self, lat: float, lon: float, days: int = 5) -> ForecastResponse:
        """
        จัดการข้อมูลพยากรณ์อากาศล่วงหน้าและการวิเคราะห์ข้อมูลเบื้องต้น ((2)) ((16)).
        """
        geocode = f"{lat},{lon}"
        cache_key = f"forecast:{days}d:{geocode}"

        # ตรวจสอบ Cache สำหรับข้อมูลพยากรณ์อากาศ (TTL นานกว่าข้อมูลปัจจุบัน) ((9))
        cached_forecast = await self.cache.get(cache_key)
        if cached_forecast:
            return ForecastResponse(**cached_forecast)

        raw_forecast = await self.client.get_forecast(geocode, days=days)
        
        # ปรับแต่งข้อมูลดิบให้เป็นโครงสร้างที่ Frontend ใช้งานง่าย ((5)) ((30))
        refined_forecast = self._process_forecast_data(raw_forecast)
        
        await self.cache.set(cache_key, refined_forecast.dict(), ttl=3600)
        return refined_forecast

    def _normalize_current_weather(self, data: Dict) -> WeatherResponse:
        """
        Helper method สำหรับการแปลงรูปแบบข้อมูลดิบจาก API ให้เป็นมาตรฐานของแอปพลิเคชัน ((22)) ((33)).
        """
        # ตัวอย่างการดึงค่าจากโครงสร้างข้อมูลของ Weather Company ((8)) ((10))
        observations = data.get("observations", [{}])[0]
        return WeatherResponse(
            temperature=observations.get("temp"),
            humidity=observations.get("precip_avg"),
            condition=observations.get("wx_phrase"),
            timestamp=datetime.utcnow(),
            location_source="TWC_API"
        )

    def _process_forecast_data(self, data: Dict) -> ForecastResponse:
        """
        กระบวนการประมวลผลข้อมูลพยากรณ์เพื่อใช้ในการทำ Data Analysis ((5)) ((15)).
        """
        # สร้าง Logic ในการคัดกรองหรือคำนวณค่าเฉลี่ยของสภาพอากาศล่วงหน้า ((32))
        forecast_list = []
        for day in data.get("daypart", []):
            # ตรวจสอบความสมบูรณ์ของข้อมูลก่อนนำไปใช้ ((33))
            if day.get("precip_chance") is not None:
                forecast_list.append(day)
        
        return ForecastResponse(items=forecast_list, generated_at=datetime.utcnow())

    async def check_severe_alerts(self, lat: float, lon: float) -> List:
        """
        ระบบตรวจสอบการแจ้งเตือนสภาพอากาศที่เป็นอันตราย ((18)) ((36)).
        """
        geocode = f"{lat},{lon}"
        raw_alerts = await self.client.get_weather_alerts(geocode)
        
        # กรองเฉพาะการแจ้งเตือนที่มีความสำคัญสูงเพื่อส่งต่อไปยังระบบ Notification ((31))
        active_alerts = [
            WeatherAlert(**alert) for alert in raw_alerts.get("alerts", [])
            if alert.get("severity") in ["Extreme", "Severe"]
        ]
        return active_alerts
```

#### รายละเอียดการนำไปใช้งาน (Implementation Details)
ในส่วนของ WeatherService นี้ เรามุ่งเน้นไปที่การสร้างความสมดุลระหว่างประสิทธิภาพ (Performance) และความถูกต้องของข้อมูล (Data Accuracy) โดยมีหลักการสำคัญดังนี้ ((9)) ((34)):

- **Multi-Level Caching**: การใช้ Caching Strategy ที่แยกตามประเภทข้อมูลช่วยลดภาระของ API ภายนอกได้อย่างมาก โดยข้อมูลปัจจุบันจะถูกเก็บไว้สั้นๆ (Short-lived) ในขณะที่ข้อมูลพยากรณ์จะถูกเก็บไว้นานขึ้น (Long-lived) เนื่องจากมีการเปลี่ยนแปลงไม่บ่อยนัก ((7)) ((9)).
- **Data Normalization**: เนื่องจากข้อมูลจาก The Weather Company อาจมีโครงสร้างที่ซับซ้อนและมีการเปลี่ยนแปลงได้ ชั้น Service นี้จึงทำหน้าที่เป็นเกราะป้องกัน (Anti-Corruption Layer) โดยการตรวจสอบและแปลงข้อมูลให้อยู่ในรูปแบบ Pydantic Models ของเราเองก่อนส่งต่อไปยังชั้นอื่น ((22)) ((33)).
- **Asynchronous Data Ingestion**: เพื่อรองรับการทำ Data Analysis และ Machine Learning ในอนาคต ทุกครั้งที่มีการเรียกข้อมูลใหม่ Service จะส่งข้อมูลนั้นไปยัง Background Worker (เช่น Celery หรือ FastAPI Background Tasks) เพื่อบันทึกลงในระบบจัดเก็บข้อมูลระยะยาวโดยไม่หน่วงเวลาการตอบสนองของ User ((19)) ((21)).
- **Resilience & Fallback**: มีการออกแบบให้ระบบสามารถทำงานต่อได้แม้เกิดข้อผิดพลาดในการดึงข้อมูลบางส่วน เช่น การดึงค่าจาก Cache เดิมหาก API ล่ม หรือการใช้ข้อมูลพยากรณ์ที่มีอยู่มาเป็นค่าอ้างอิงชั่วคราว ((1)) ((17)).
- **Business Logic Integration**: ชั้นนี้คือที่สำหรับใส่สูตรคำนวณเฉพาะทาง เช่น การคำนวณดัชนีความร้อน (Heat Index) หรือความเสี่ยงจากสภาพอากาศ (Weather Risk Score) ซึ่งเป็นข้อมูลเชิงลึกที่เหนือกว่าแค่ข้อมูลดิบจาก API ((15)) ((32)).

"""
หัวข้อที่คุณอาจอยากดูต่อ:
- UseweatherAPIfordataanalysis: การนำข้อมูลอากาศมาวิเคราะห์เพื่อการตัดสินใจทางธุรกิจ
- Cachingstrategy: เทคนิคการตั้งค่า Redis และ TTL สำหรับงาน Weather Data
- Data Normalization: แนวทางการออกแบบ Schema ให้ยืดหยุ่นต่อการเปลี่ยนแปลงของ Provider
- Machine Learning Pipeline: การเตรียมข้อมูล Weather Features สำหรับโมเดลทำนายผล
"""

### app/routers/weather_router.py

ในส่วนของ weather_router.py ทำหน้าที่เป็นประตูทางเข้าหลัก (Entry Point) สำหรับการสื่อสารผ่านเครือข่าย โดยทำหน้าที่เป็นหน่วยควบคุม (Controller) ที่รับคำขอ HTTP Request จากผู้ใช้งานหรือระบบอื่น แล้วส่งต่อไปยัง WeatherService เพื่อประมวลผลตามหลักการของ FastAPI{{7}} ที่เน้นความเร็วและมาตรฐาน REST API ((12)) ((33)). โครงสร้างนี้ถูกออกแบบให้รองรับทั้งการดึงข้อมูลแบบเรียลไทม์และการเรียกดูข้อมูลภาพเชิงซ้อน (Imagery) โดยมีการจัดการระบบรักษาความปลอดภัยและการตรวจสอบข้อมูล (Validation) อย่างเข้มงวด ((20)) ((33)).

```python
"""
Guided Links:
- Buildweatherapp:
- Fastapi-production-best-practices: [Security & Deployment Link]
- Weather-api-documentation:
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from app.services.weather_service import WeatherService
from app.schemas.weather import WeatherResponse, ForecastResponse, WeatherAlert, ImageryLayer
from app.config.weather_settings import settings
from app.utils.rate_limiter import RateLimitExceeded

# การกำหนด Router พร้อม Prefix และ Tags เพื่อจัดระเบียบใน OpenAPI (Swagger) UI ((12)) ((33))
router = APIRouter(
    prefix="/weather",
    tags=["Weather Intelligence"],
    responses={404: {"description": "Weather data not found"}}
)

# การทำ Dependency Injection สำหรับ WeatherService เพื่อให้ง่ายต่อการทำ Unit Testing ((6)) ((33))
def get_weather_service() -> WeatherService:
    from app.clients.weathercompanyclient import WeatherCompanyClient
    client = WeatherCompanyClient()
    return WeatherService(client)

@router.get("/current", response_model=WeatherResponse)
async def get_current_weather(
    lat: float = Query(..., description="Latitude ของตำแหน่งที่ต้องการตรวจสอบ"),
    lon: float = Query(..., description="Longitude ของตำแหน่งที่ต้องการตรวจสอบ"),
    service: WeatherService = Depends(get_weather_service)
):
    """
    ดึงข้อมูลสภาพอากาศปัจจุบัน (Current Conditions) ((4)) ((23)).
    - รับค่าพิกัดพิกัดภูมิศาสตร์ (Geocode)
    - ส่งคืนข้อมูลอุณหภูมิ, ความชื้น และสภาพท้องฟ้า
    """
    try:
        return await service.get_weather_status(lat, lon)
    except RateLimitExceeded:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="การเรียกใช้ API เกินขีดจำกัดที่กำหนด"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"เกิดข้อผิดพลาดในการดึงข้อมูลอากาศ: {str(e)}"
        )

@router.get("/forecast", response_model=ForecastResponse)
async def get_weather_forecast(
    lat: float,
    lon: float,
    days: int = Query(5, ge=1, le=15, description="จำนวนวันที่ต้องการพยากรณ์ (สูงสุด 15 วัน)"),
    service: WeatherService = Depends(get_weather_service)
):
    """
    พยากรณ์อากาศล่วงหน้า (Daily Forecast) ((2)) ((13)).
    - รองรับการกำหนดจำนวนวันพยากรณ์ได้สูงสุด 15 วันตามข้อกำหนดของ Weather Company ((35)).
    - ใช้ข้อมูลเชิงวิเคราะห์เพื่อช่วยในการตัดสินใจทางธุรกิจ ((2)).
    """
    return await service.get_extended_forecast(lat, lon, days=days)

@router.get("/alerts", response_model=List)
async def get_active_alerts(
    lat: float,
    lon: float,
    service: WeatherService = Depends(get_weather_service)
):
    """
    ตรวจสอบการแจ้งเตือนภัยพิบัติและสภาพอากาศรุนแรง (Weather Alerts) ((18)) ((36)).
    - ส่งคืนรายการการแจ้งเตือนที่กำลังมีผลบังคับใช้ในพื้นที่นั้นๆ
    """
    alerts = await service.check_severe_alerts(lat, lon)
    if not alerts:
        return []
    return alerts

@router.get("/imagery", response_model=ImageryLayer)
async def get_weather_imagery(
    product: str = Query("radar", regex="^(radar|satellite|precipitation)$"),
    zoom: int = Query(6, ge=1, le=20),
    x: int = Query(...),
    y: int = Query(...),
    service: WeatherService = Depends(get_weather_service)
):
    """
    ดึงข้อมูลภาพแผนที่อากาศ (Imagery Layer) ในรูปแบบพิกัด Tile ((25)) ((36)).
    - รองรับผลิตภัณฑ์ประเภทรดาร์ (Radar), ดาวเทียม (Satellite) และปริมาณฝน (Precipitation).
    - ข้อมูลถูกออกแบบมาเพื่อใช้ร่วมกับแผนที่แบบ Interactive เช่น Mapbox หรือ Leaflet ((25)).
    """
    # ในระดับ Router จะส่งคืนรายละเอียด Metadata หรือ Proxy URL สำหรับการแสดงผลภาพ
    return await service.prepare_imagery_metadata(product, x, y, zoom)
```

#### รายละเอียดการนำไปใช้งาน (Implementation Details)
การออกแบบ weather_router.py ในระบบนี้ให้ความสำคัญกับมาตรฐานอุตสาหกรรมและการรองรับการขยายตัว (Scalability) ดังนี้ ((1)) ((9)):

- **Request Validation**: การใช้ `Query` และ `Pydantic` (ผ่าน `response_model`) ช่วยให้แน่ใจว่าข้อมูลที่รับเข้ามาและส่งออกไปมีความถูกต้องตามโครงสร้างที่กำหนดไว้ ลดโอกาสเกิดข้อผิดพลาดรันไทม์ในระดับแอปพลิเคชัน ((33)).
- **Dependency Injection (DI)**: การทำ DI ของ `WeatherService` ช่วยให้ Router ไม่ต้องรับผิดชอบเรื่องการสร้างอ็อบเจกต์ Client หรือ Service ด้วยตัวเอง ทำให้โค้ดมีความยืดหยุ่น (Loosely Coupled) และง่ายต่อการเขียนการทดสอบแบบ Mocking ((6)) ((17)).
- **HTTP Semantics & Error Handling**: มีการเลือกใช้ HTTP Status Codes อย่างเหมาะสม เช่น `429` สำหรับการเกินขีดจำกัดการเรียกใช้งาน และ `500` สำหรับข้อผิดพลาดจากฝั่ง Server ของ Provider เพื่อให้ผู้ใช้งาน API ฝั่ง Frontend สามารถจัดการ Error ได้อย่างถูกต้อง ((8)) ((20)).
- **Endpoint Granularity**: การแยก Endpoint ตามประเภทของข้อมูลอากาศ (Current, Forecast, Alerts, Imagery) ช่วยให้ระบบมีความชัดเจนในการเรียกใช้งาน และช่วยในเรื่องการจัดการสิทธิ์เข้าถึง (Access Control) ของแต่ละกลุ่มผู้ใช้งานได้ในอนาคต ((32)) ((33)).
- **Asynchronous Flow**: ทุก Route ถูกกำหนดเป็น `async def` เพื่อใช้ประโยชน์จาก Non-blocking I/O ของ FastAPI{{7}} ซึ่งจำเป็นมากเมื่อต้องรอข้อมูลจาก API ภายนอกอย่าง The Weather Company ที่อาจมี Latency ที่แปรผัน ((12)) ((29)).
- **Documentation Integration**: การใช้ `tags` และ `description` ใน Router ช่วยสร้างคู่มือการใช้งานแบบอัตโนมัติผ่าน Swagger UI ทำให้ทีมพัฒนา Frontend หรือนักพัฒนาภายนอกสามารถทำความเข้าใจ API ได้โดยไม่ต้องอ่านเอกสารแยกต่างหาก ((12)) ((22)).

หัวข้อที่คุณอาจอยากดูต่อ:
- Buildweatherapp: การสร้างแอปพลิเคชันที่รองรับการแสดงผลข้อมูลอากาศแบบครบวงจร
- FastAPI Router: เจาะลึกการจัดโครงสร้าง Router สำหรับโครงการขนาดใหญ่
- REST API Best Practices: แนวทางปฏิบัติในการออกแบบ Endpoint ให้เป็นสากล
- Interactive Weather Maps: เทคนิคการเชื่อมต่อ Imagery Layer เข้ากับแผนที่บนเว็บและแอปพลิเคชัน

### app/schemas/weather.py

```python
"""
Guided Links:
- ExplainweatherAPIusecases:
- Pydantic-validation-guide:
- Fastapi-response-modeling:
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class WeatherBase(BaseModel):
    """
    หน้าที่ (Responsibility): 
    - เป็นคลาสพื้นฐานสำหรับข้อมูลสภาพอากาศทั้งหมด เพื่อกำหนดค่าคอนฟิกูเรชันเริ่มต้น ((12)) ((33)).
    - ใช้ประโยชน์จาก Type Hinting ของ Python เพื่อให้ IDE ตรวจสอบความถูกต้องของข้อมูลได้ ((12)).
    """
    class Config:
        orm_mode = True # รองรับการทำงานร่วมกับ Database models ในอนาคต ((6))
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "location": "Bangkok",
                "provider": "The Weather Company"
            }
        }

class WeatherResponse(WeatherBase):
    """
    หน้าที่ (Responsibility):
    - กำหนดโครงสร้างข้อมูลสำหรับสภาพอากาศปัจจุบัน (Current Conditions) ((4)) ((23)).
    - ทำหน้าที่เป็น JSON Schema สำหรับการส่งออกข้อมูลผ่าน API ((33)).
    """
    temperature: float = Field(..., description="อุณหภูมิปัจจุบันในหน่วยเซลเซียส", example=32.5)
    feels_like: Optional = Field(None, description="อุณหภูมิที่รู้สึกได้จริง (Heat Index)")
    humidity: int = Field(..., ge=0, le=100, description="ความชื้นสัมพัทธ์ในหน่วยเปอร์เซ็นต์ ((31))")
    condition: str = Field(..., description="คำอธิบายสภาพอากาศสั้นๆ เช่น 'Cloudy' หรือ 'Rain' ((10))")
    wind_speed: float = Field(..., description="ความเร็วลมในหน่วยกิโลเมตรต่อชั่วโมง")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="เวลาที่บันทึกข้อมูล ((32))")

    @validator('temperature')
    def validate_temp(cls, v):
        # ตรวจสอบความสมเหตุสมผลของข้อมูลอุณหภูมิเพื่อป้องกันความผิดพลาดจากต้นทาง ((33))
        if v < -100 or v > 70:
            raise ValueError('อุณหภูมิไม่อยู่ในเกณฑ์ที่เป็นไปได้ตามธรรมชาติ')
        return v

class ForecastItem(BaseModel):
    """
    หน้าที่ (Responsibility):
    - จัดเก็บข้อมูลพยากรณ์อากาศรายวันหรือรายชั่วโมง ((2)) ((13)).
    - รองรับการทำ Data Validation สำหรับข้อมูลชุดล่วงหน้าที่มีความซับซ้อน ((1)) ((33)).
    """
    date: str = Field(..., description="วันที่พยากรณ์ (YYYY-MM-DD)")
    temp_max: float = Field(..., description="อุณหภูมิสูงสุดที่คาดการณ์ ((13))")
    temp_min: float = Field(..., description="อุณหภูมิต่ำสุดที่คาดการณ์ ((23))")
    precip_chance: int = Field(..., ge=0, le=100, description="โอกาสที่จะเกิดฝนในรูปแบบเปอร์เซ็นต์ ((32))")
    summary: str = Field(..., description="สรุปสภาพอากาศประจำวัน ((4))")

class ForecastResponse(WeatherBase):
    """
    หน้าที่ (Responsibility):
    - รวบรวมรายการพยากรณ์อากาศทั้งหมดสำหรับการส่งคืนค่าแบบรายการ ((13)) ((16)).
    - จัดเตรียมข้อมูลสรุป (Metadata) สำหรับชุดข้อมูลพยากรณ์ ((15)) ((33)).
    """
    location_name: str = Field(..., description="ชื่อสถานที่หรือพิกัดภูมิศาสตร์ ((28))")
    forecast_days: List = Field(..., description="รายการข้อมูลพยากรณ์ล่วงหน้ารายวัน ((2)) ((32))")
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class WeatherAlert(BaseModel):
    """
    หน้าที่ (Responsibility):
    - โครงสร้างข้อมูลสำหรับการแจ้งเตือนภัยพิบัติและสภาวะรุนแรง ((18)) ((36)).
    - ช่วยให้ระบบปลายทางสามารถคัดกรองความรุนแรงของการแจ้งเตือนได้โดยง่าย ((31)).
    """
    event: str = Field(..., description="ชื่อประเภทเหตุการณ์ เช่น 'Flood Warning' หรือ 'Heat Advisory'")
    severity: str = Field(..., description="ระดับความรุนแรง (Minor, Moderate, Severe, Extreme) ((31))")
    description: str = Field(..., description="รายละเอียดและคำแนะนำสำหรับการรับมือ ((18))")
    expiry: datetime = Field(..., description="วันเวลาที่การแจ้งเตือนนี้จะสิ้นสุดลง ((8))")

class ImageryLayer(BaseModel):
    """
    หน้าที่ (Responsibility):
    - จัดการ Metadata สำหรับข้อมูลภาพถ่ายดาวเทียมและเรดาร์ ((25)) ((36)).
    - ให้ข้อมูลพิกัด Tile สำหรับการแสดงผลบนหน้าจอ Dashboard ((11)) ((25)).
    """
    product_type: str = Field(..., description="ประเภทของเลเยอร์ เช่น 'radar_past' หรือ 'satellite_ir' ((25))")
    tile_url_template: str = Field(..., description="URL Template สำหรับการเรียกใช้ภาพแผนที่ ((10))")
    zoom_levels: List = Field(default=, description="ระดับการซูมที่รองรับ ((25))")
```

ในระบบ FastAPI{{7}} การกำหนด schemas หรือ Pydantic models ถือเป็นส่วนสำคัญที่สุดในการสร้าง API ที่มีประสิทธิภาพและปลอดภัย ((12)) ((33)). ชั้นนี้ไม่ได้เป็นเพียงแค่การกำหนดรูปแบบข้อมูล แต่ยังเป็นตัวขับเคลื่อนหลักสำหรับกระบวนการตรวจสอบข้อมูลแบบอัตโนมัติ (Automated Data Validation) ซึ่งจะช่วยคัดกรองข้อมูลที่ไม่สมบูรณ์จาก The Weather Company API ก่อนที่จะถูกนำไปประมวลผลในชั้น Service ((1)) ((9)). 

การใช้โครงสร้างแบบสืบทอด (Inheritance) ใน `WeatherBase` ช่วยลดความซ้ำซ้อนของโค้ด (DRY Principle) และทำให้การแก้ไขค่าคอนฟิกูเรชันส่วนกลางทำได้ในจุดเดียว ((6)) ((33)). นอกจากนี้ การกำหนด `Field` พร้อมรายละเอียดคำอธิบาย (Description) และตัวอย่างข้อมูล (Example) จะถูกนำไปสร้างเป็นเอกสาร OpenAPI โดยอัตโนมัติ ซึ่งมีประโยชน์อย่างยิ่งต่อทีมพัฒนา Frontend ในการทำความเข้าใจโครงสร้างข้อมูลที่ซับซ้อนของระบบอากาศ ((12)) ((22)). 

โมเดลเหล่านี้ยังรองรับการทำงานในระดับสูง เช่น การใช้ `@validator` เพื่อตรวจสอบตรรกะทางธุรกิจ (Business Logic Validation) เช่น การตรวจสอบค่าอุณหภูมิที่ผิดปกติ หรือการตรวจสอบเปอร์เซ็นต์ความชื้นให้อยู่ในช่วง 0 ถึง 100 เสมอ ((31)) ((33)). ความเข้มงวดในระดับ Schema นี้จะช่วยให้มั่นใจได้ว่าข้อมูลที่จะถูกนำไปใช้งานในส่วนของ Machine Learning หรือการทำ Data Analysis จะมีความสะอาดและแม่นยำตั้งแต่ต้นน้ำ ((5)) ((15)). 

การแยกโมเดลสำหรับการแจ้งเตือน (`WeatherAlert`) และข้อมูลภาพ (`ImageryLayer`) ออกจากข้อมูลสภาพอากาศทั่วไป ช่วยให้ระบบมีความยืดหยุ่นสูง (High Granularity) ((32)) ((36)). ซึ่งจะอำนวยความสะดวกในการขยายขีดความสามารถของแอปพลิเคชันในอนาคต เช่น การเพิ่มฟีเจอร์วิเคราะห์ความเสี่ยงรายพื้นที่ หรือการพยากรณ์อากาศแบบ Hyperlocal ที่ต้องการความละเอียดของข้อมูลที่แตกต่างกันไปตามแต่ละ Use Case ((4)) ((21)) ((34)).

### app/config/weather_settings.py

ในโครงสร้างของ FastAPI boilerplate{{2}} การจัดการการตั้งค่า (Configuration Management) ถือเป็นรากฐานสำคัญที่ช่วยให้ระบบมีความปลอดภัยและยืดหยุ่นต่อการเปลี่ยนแปลงสภาพแวดล้อมในการทำงาน (Environment) ((6)) ((33)). สำหรับการรวม The Weather Company API{{1}} เข้ากับระบบ ไฟล์ `app/config/weather_settings.py` จะทำหน้าที่เป็นศูนย์กลางในการเก็บรวบรวมค่ากำหนดทั้งหมดที่จำเป็น ตั้งแต่รหัสผ่านการเข้าถึง (API Credentials) ไปจนถึงการตั้งค่าประสิทธิภาพของเครือข่าย ((14)) ((20)). การใช้ Pydantic Settings ช่วยให้นักพัฒนาสามารถดึงค่าจากไฟล์ `.env` ได้อย่างเป็นระบบ พร้อมทั้งมีการตรวจสอบประเภทข้อมูล (Type Validation) โดยอัตโนมัติ เพื่อป้องกันข้อผิดพลาดที่อาจเกิดขึ้นจากการตั้งค่าที่ไม่ถูกต้องก่อนที่แอปพลิเคชันจะเริ่มทำงาน ((12)) ((33)).

```python
"""
Guided Links:
- ChoosebestweatherAPIformyproject: [API Comparison & Tier Guide Link]
- Fastapi-configuration-management:
- Weather-api-security-best-practices:
"""

import os
from pydantic import BaseSettings, Field, HttpUrl
from typing import Optional

class WeatherSettings(BaseSettings):
    """
    หน้าที่ (Responsibility):
    - จัดเก็บและจัดการการตั้งค่าทั้งหมดที่เกี่ยวข้องกับ Weather Company API ((8)) ((32)).
    - อ่านค่าจาก Environment Variables หรือไฟล์ .env เพื่อความปลอดภัยของข้อมูลสำคัญ ((14)) ((33)).
    - กำหนดค่าเริ่มต้น (Default Values) และโครงสร้างที่จำเป็นสำหรับการเชื่อมต่อเครือข่าย ((1)) ((9)).
    """

    # --- API Credentials & Identity ---
    # ข้อมูลเหล่านี้เป็นความลับระดับสูง (Sensitive Data) ห้ามใส่ค่าจริงลงในโค้ด ((14))
    WEATHER_API_KEY: str = Field(..., env="WEATHER_API_KEY")
    WEATHER_CLIENT_ID: Optional = Field(None, env="WEATHER_CLIENT_ID")
    WEATHER_ORG_ID: Optional = Field(None, env="WEATHER_ORG_ID")

    # --- API Endpoint Configuration ---
    # ใช้ HttpUrl เพื่อตรวจสอบความถูกต้องของ URL ตั้งแต่ขั้นตอนโหลดแอปพลิเคชัน ((12)) ((33))
    WEATHER_API_BASE_URL: HttpUrl = Field(
        ".com", 
        env="WEATHER_API_BASE_URL"
    )
    
    # สำหรับบริการ Imagery หรือ Data Lake เฉพาะทางอาจใช้ Domain ที่แตกต่างกัน ((19)) ((25))
    WEATHER_DATA_DOMAIN: str = Field("api.weather.com", env="WEATHER_DATA_DOMAIN")

    # --- Connection & Performance Settings ---
    # การตั้งค่า Timeout และ Retry เป็นสิ่งจำเป็นสำหรับระบบที่ต้องเชื่อมต่อกับ API ภายนอก ((1)) ((17))
    WEATHER_API_TIMEOUT: float = Field(30.0, description="ระยะเวลารอการตอบสนองสูงสุดในหน่วยวินาที")
    WEATHER_MAX_RETRIES: int = Field(3, description="จำนวนครั้งที่ระบบจะพยายามเรียก API ใหม่เมื่อเกิดข้อผิดพลาด")
    WEATHER_POOL_SIZE: int = Field(10, description="จำนวน Connection สูงสุดใน HTTP Pool")

    # --- Cache & Rate Limiting Settings ---
    # การตั้งค่าเหล่านี้ช่วยควบคุมต้นทุนการใช้งาน API (API Cost Management) ((9)) ((13))
    WEATHER_CACHE_TTL_CURRENT: int = Field(900, description="อายุของ Cache สำหรับข้อมูลปัจจุบัน (15 นาที)")
    WEATHER_CACHE_TTL_FORECAST: int = Field(3600, description="อายุของ Cache สำหรับข้อมูลพยากรณ์ (1 ชั่วโมง)")
    
    # อ้างอิงจากแผนการใช้งาน (Usage Plan) ของ Weather Company API ((21)) ((27))
    WEATHER_RATE_LIMIT_PER_MINUTE: int = Field(100, env="WEATHER_RATE_LIMIT_PER_MINUTE")

    class Config:
        # กำหนดชื่อไฟล์ .env ที่จะให้อ่านค่า และความละเอียดในการพิมพ์ตัวเล็กใหญ่ (Case Sensitivity) ((33))
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# สร้างอ็อบเจกต์ settings เพียงครั้งเดียวเพื่อใช้ร่วมกันทั้งแอปพลิเคชัน (Singleton Pattern) ((17))
weather_settings = WeatherSettings()
```

#### รายละเอียดเชิงลึกและการนำไปใช้งาน (Detailed Implementation)

การออกแบบโครงสร้าง weather_settings.py ในระดับองค์กรจำเป็นต้องรองรับความซับซ้อนของการใช้งานจริง โดยมีรายละเอียดที่สำคัญดังนี้ ((16)) ((20)):

**1. ระบบรักษาความปลอดภัยของข้อมูล (Security Architecture)**
การดึงข้อมูลผ่าน The Weather Company API{{1}} มักต้องการการรับรองตัวตน (Authentication) ที่เข้มงวด เช่น การใช้ API Key หรือในบางกรณีอาจต้องใช้ Basic JWT Authentication ซึ่งประกอบด้วย Client ID และ Organization ID ((14)) ((19)). การใช้ `BaseSettings` ช่วยให้เรามั่นใจได้ว่าข้อมูลเหล่านี้จะไม่ถูกเก็บไว้ในเวอร์ชันคอนโทรล (Git) แต่จะถูกโหลดผ่านระบบสภาพแวดล้อมที่ปลอดภัยแทน ((33)).

**2. การจัดการความพร้อมใช้งาน (Network Resilience)**
ในการเชื่อมต่อกับบริการคลาวด์ภายนอก การตั้งค่า `WEATHER_API_TIMEOUT` และ `WEATHER_MAX_RETRIES` มีบทบาทสำคัญในการป้องกันเหตุการณ์ Cascading Failure ((1)). หาก API ต้นทางมีความล่าช้า การกำหนด Timeout ที่เหมาะสมจะช่วยให้ระบบ FastAPI{{7}} สามารถคืนทรัพยากรไปจัดการคำขออื่นต่อได้ และการใช้ระบบ Retry ที่มีการเว้นระยะเวลา (Exponential Backoff) จะช่วยลดผลกระทบจากการขัดข้องชั่วคราวของเครือข่าย ((17)) ((20)).

**3. การควบคุมต้นทุนและประสิทธิภาพ (Performance & Cost Optimization)**
The Weather Company มักมีการคิดค่าบริการตามจำนวนครั้งที่เรียกใช้ (Calls per Minute/Month) ((21)) ((27)). การกำหนดค่า `WEATHER_CACHE_TTL` แยกตามประเภทข้อมูล (Current vs Forecast) ในไฟล์ตั้งค่านี้ จะช่วยให้ชั้น WeatherService สามารถตัดสินใจได้ว่าเมื่อใดควรดึงข้อมูลใหม่ และเมื่อใดควรใช้ข้อมูลเดิมจากระบบ Cache ((7)) ((9)). นอกจากนี้ การตั้งค่า `WEATHER_RATE_LIMIT_PER_MINUTE` ยังทำหน้าที่เป็นเกราะป้องกันชั้นแรกไม่ให้แอปพลิเคชันของเรายิงคำขอเกินโควตาที่สมัครไว้ ซึ่งอาจนำไปสู่การถูกระงับบริการชั่วคราว ((9)).

**4. การแยกแยะสภาพแวดล้อม (Multi-environment Support)**
ด้วยโครงสร้างนี้ นักพัฒนาสามารถเปลี่ยนเป้าหมายการเชื่อมต่อจาก Sandbox หรือ Mock API ไปยัง Production API ได้อย่างง่ายดายเพียงแค่แก้ไขไฟล์ `.env` โดยไม่ต้องแตะต้องโค้ดหลัก ((6)). เช่น การเปลี่ยน `WEATHER_API_BASE_URL` จากเครื่องมือทดสอบไปยัง URL จริงของ IBM ที่ใช้ในอุตสาหกรรมรถยนต์หรือประกันภัย ((16)) ((32)).

**5. ความสามารถในการขยายตัว (Extensibility)**
หากในอนาคตมีการเพิ่มเลเยอร์ข้อมูลใหม่ๆ เช่น ข้อมูลภาพถ่ายดาวเทียมความละเอียดสูง (Imagery Layer) หรือข้อมูลประวัติย้อนหลัง (Historical Data) เราสามารถเพิ่มฟิลด์การตั้งค่าใหม่ๆ ลงใน `WeatherSettings` ได้ทันที โดยที่ยังคงรักษามาตรฐานการตรวจสอบข้อมูลและความปลอดภัยเดิมไว้ ((10)) ((25)) ((36)).

"""
หัวข้อที่คุณอาจอยากดูต่อ:
- ChoosebestweatherAPIformyproject: แนวทางการเลือก Package ของ Weather Company ที่เหมาะกับงบประมาณ
- FastAPI Configuration: เจาะลึกการใช้ Pydantic Settings สำหรับโครงการขนาดใหญ่
- API Authentication Patterns: รูปแบบการจัดการ JWT และ OAuth2 ในระบบ API ภายนอก
- Environment Variable Security: วิธีการเก็บรักษาความลับของระบบในกระบวนการ CI/CD
"""

### app/utils/cache.py

```python
"""
Guided Links:
- Cachingstrategy:
- IntegrateweatherAPIintobackend:
- Weathermicroservice:
"""

import json
import logging
from typing import Any, Optional, Union
from datetime import timedelta
import redis.asyncio as redis
from app.config.weather_settings import settings

# การตั้งค่า Logging สำหรับตรวจสอบสถานะการทำงานของระบบ Cache ((6))
logger = logging.getLogger(__name__)

class WeatherCache:
    """
    หน้าที่ (Responsibility):
    - เป็น Wrapper สำหรับการจัดการ Redis หรือ In-memory cache เพื่อเพิ่มประสิทธิภาพระบบ ((7)) ((9)).
    - ลดค่าใช้จ่ายในการเรียกใช้งานภายนอกและเพิ่มความเร็วในการตอบสนอง (Latency) ((1)) ((9)).
    - จัดการระบบ Time-to-Live (TTL) แยกตามประเภทข้อมูลสภาพอากาศ ((32)) ((33)).
    """

    def __init__(self):
        # การสร้างการเชื่อมต่อแบบ Async เพื่อรองรับประสิทธิภาพสูงสุดใน FastAPI{{7}} ((12)) ((20))
        self.redis_client: Optional = None
        self.cache_enabled = True

    async def connect(self):
        """เริ่มต้นการเชื่อมต่อกับระบบ Redis ((20))"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL, 
                encoding="utf-8", 
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("เชื่อมต่อระบบ Redis สำเร็จสำหรับการจัดการข้อมูลอากาศ")
        except Exception as e:
            logger.error(f"ไม่สามารถเชื่อมต่อ Redis ได้: {str(e)} ระบบจะทำงานแบบไม่มี Cache")
            self.cache_enabled = False

    async def get(self, key: str) -> Optional:
        """ดึงข้อมูลจาก Cache โดยใช้ Key ((30)) ((33))"""
        if not self.cache_enabled or not self.redis_client:
            return None
        
        try:
            data = await self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.warning(f"เกิดข้อผิดพลาดในการดึงข้อมูลจาก Cache: {str(e)}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        """บันทึกข้อมูลลงใน Cache พร้อมกำหนดอายุการใช้งาน ((7)) ((9))"""
        if not self.cache_enabled or not self.redis_client:
            return

        try:
            await self.redis_client.set(
                key, 
                json.dumps(value), 
                ex=ttl
            )
        except Exception as e:
            logger.error(f"ไม่สามารถบันทึกข้อมูลลง Cache ได้: {str(e)}")

    async def delete(self, key: str):
        """ลบข้อมูลใน Cache เมื่อข้อมูลมีการเปลี่ยนแปลงหรือหมดอายุ ((33))"""
        if self.redis_client:
            await self.redis_client.delete(key)

    def generate_key(self, prefix: str, *args) -> str:
        """สร้าง Cache Key ที่เป็นมาตรฐานสำหรับระบบ ((6)) ((33))"""
        suffix = ":".join(str(arg) for arg in args)
        return f"weather:{prefix}:{suffix}"
```

การพัฒนาระบบภูมิอากาศที่มีความน่าเชื่อถือสูงจำเป็นต้องอาศัยกลยุทธ์การจัดเก็บข้อมูลชั่วคราวที่มีประสิทธิภาพเพื่อจัดการกับข้อจำกัดของ The Weather Company API{{1}} และเพื่อปรับปรุงประสบการณ์ของผู้ใช้งาน ((1)) ((9)). ไฟล์ `app/utils/cache.py` นี้ทำหน้าที่เป็นตัวกลางในการจัดการข้อมูลด้วยรูปแบบ Cache-Aside ซึ่งเป็นมาตรฐานในการพัฒนาเว็บแอปพลิเคชันสมัยใหม่ที่ต้องการความเร็วและการปรับขยายตัวที่มีประสิทธิภาพ ((17)) ((20)).

การเลือกใช้ Redis เป็นระบบหลักในการทำ Caching ช่วยให้แอปพลิเคชันสามารถรักษาความเร็วในการเข้าถึงข้อมูล (High Performance) แม้ในช่วงที่มีปริมาณการใช้งานหนาแน่น โดยมีการใช้รูปแบบการเขียนโค้ดแบบไม่ปิดกั้น (Asynchronous) เพื่อให้สอดคล้องกับโครงสร้างหลักของ FastAPI{{7}} ที่เน้นการประมวลผลที่มีประสิทธิภาพสูง ((12)) ((29)). การจัดการทรัพยากรผ่าน `AsyncClient` ช่วยให้มั่นใจได้ว่าระบบจะไม่เกิดปัญหาคอขวดเมื่อต้องรับมือกับคำขอจำนวนมากพร้อมกัน ((20)).

กลยุทธ์การกำหนดอายุของข้อมูล (TTL Management) ในส่วนนี้มีความสำคัญอย่างยิ่ง เนื่องจากข้อมูลสภาพอากาศแต่ละประเภทมีอัตราการเปลี่ยนแปลงที่ไม่เท่ากัน ((32)) ((34)). ตัวอย่างเช่น ข้อมูลสภาพอากาศปัจจุบัน (Current Conditions) ควรมีค่า TTL ที่สั้นประมาณ 5 ถึง 15 นาที เพื่อให้ผู้ใช้งานได้รับข้อมูลที่ใกล้เคียงความจริงมากที่สุด ((4)) ((23)). ในขณะที่ข้อมูลพยากรณ์อากาศล่วงหน้า (Forecast) หรือข้อมูลภาพถ่ายดาวเทียม (Imagery Layers) สามารถกำหนดค่า TTL ที่นานขึ้นได้ เช่น 1 ถึง 6 ชั่วโมง เนื่องจากข้อมูลเหล่านี้ไม่มีการปรับปรุงบ่อยครั้งในระดับนาที ((13)) ((25)) ((32)).

นอกจากความเร็วแล้ว ระบบ Cache ยังช่วยในเรื่องการบริหารจัดการต้นทุน (Cost Optimization) ของแอปพลิเคชัน ((9)). เนื่องจากการเรียกใช้งาน The Weather Company API{{1}} มักมีค่าใช้จ่ายตามจำนวนครั้งที่เรียกใช้หรือมีโควตาจำกัดต่อนาที ((21)) ((27)). การใช้ระบบตรวจสอบข้อมูลใน Cache ก่อนการเรียก API จริงจะช่วยลดจำนวนคำขอที่ไม่จำเป็นลงได้อย่างมหาศาล ซึ่งเป็นแนวทางปฏิบัติที่ดีที่สุด (Best Practice) สำหรับการผสานรวม API ภายนอกในระดับองค์กร ((6)) ((9)).

ในด้านความปลอดภัยและการรักษาความสมบูรณ์ของข้อมูล (Data Integrity) ตัว Wrapper นี้ยังรองรับการทำ Serialization ข้อมูลเป็นรูปแบบ JSON เพื่อให้ง่ายต่อการจัดเก็บและดึงกลับมาใช้งานใหม่ โดยยังคงรักษาโครงสร้างของชุดข้อมูล (Data Types) ไว้อย่างถูกต้องตามข้อกำหนดของภาษา Python ((12)) ((33)). นอกจากนี้ยังมีการออกแบบระบบ Error Handling ที่ยืดหยุ่น โดยหากระบบ Redis เกิดขัดข้อง แอปพลิเคชันจะยังคงสามารถทำงานต่อไปได้โดยการดึงข้อมูลจาก API โดยตรงแทน (Fallback mechanism) เพื่อให้มั่นใจได้ว่าผู้ใช้งานจะยังคงสามารถเข้าถึงข้อมูลสภาพอากาศได้ตลอดเวลา ((1)) ((8)).

ท้ายที่สุด การจัดโครงสร้างไฟล์ในรูปแบบที่แยกส่วน (Modular) เช่นนี้ ช่วยให้นักพัฒนาสามารถปรับเปลี่ยนจากระบบ Redis ไปเป็น In-memory cache สำหรับสภาพแวดล้อมการทดสอบ (Testing Environment) ได้อย่างง่ายดายโดยไม่ต้องแก้ไขโค้ดในส่วนอื่นของระบบ ((6)) ((33)). ความยืดหยุ่นนี้เป็นปัจจัยสำคัญในการสร้างระบบที่สามารถบำรุงรักษาได้ง่ายและรองรับการขยายตัวในอนาคตเมื่อความต้องการทางธุรกิจเพิ่มมากขึ้น ((16)) ((30)).

### app/utils/rate_limiter.py

การจัดการการเรียกใช้งาน API ภายนอกอย่างมีประสิทธิภาพจำเป็นต้องมีระบบ Rate Limiting เพื่อป้องกันการใช้งานเกินโควตาที่กำหนดโดยผู้ให้บริการ ซึ่งในกรณีของ The Weather Company API{{1}} มักมีข้อจำกัดด้านปริมาณการเรียกใช้ต่อนาทีหรือต่อเดือนที่เข้มงวดตามแผนบริการที่เลือกซื้อ ((9)) ((16)) ((21)). ไฟล์ `app/utils/rate_limiter.py` นี้ถูกออกแบบมาเพื่อทำหน้าที่เป็นเกราะป้องกันชั้นสุดท้ายก่อนที่คำขอจะถูกส่งออกไป เพื่อให้มั่นใจว่าแอปพลิเคชันจะทำงานอยู่ภายใต้ขีดจำกัดที่ปลอดภัยและไม่ถูกระงับการให้บริการชั่วคราวจากฝั่งผู้ให้บริการ ((8)) ((27)).

```python
"""
Guided Links:
- Ratelimitprotection:
- Cachingstrategy:
- Fastapi-production-best-practices:
"""

import time
import asyncio
import logging
from typing import Optional
from fastapi import HTTPException, status
from app.config.weather_settings import settings

# การกำหนดค่า Logging เพื่อติดตามสถานะการใช้งาน Quota ในระดับ Production ((6)) ((20))
logger = logging.getLogger(__name__)

class RateLimitExceeded(Exception):
    """Exception สำหรับกรณีที่การเรียกใช้งานเกินขีดจำกัดที่กำหนดไว้ ((8))"""
    pass

class WeatherRateLimiter:
    """
    หน้าที่ (Responsibility):
    - ป้องกันการส่งคำขอไปยัง Weather Company API เกินจำนวนโควตาที่กำหนด (Quota Protection) ((9)) ((21)).
    - ใช้งานอัลกอริทึม Token Bucket หรือ Sliding Window เพื่อควบคุมปริมาณ Traffic ((17)) ((30)).
    - ทำการ Throttling หรือชะลอคำขอเพื่อให้สอดคล้องกับขีดจำกัดความเร็ว (Rate Limit) ((1)) ((33)).
    - รองรับการทำ Fallback Data ในกรณีที่คำขอถูกจำกัดเพื่อรักษาความต่อเนื่องของบริการ ((9)).
    """

    def __init__(self):
        # ดึงการตั้งค่าขีดจำกัดการใช้งานจาก Configuration Management ((33))
        self.rate_limit_per_minute = settings.WEATHER_RATE_LIMIT_PER_MINUTE
        self.tokens = float(self.rate_limit_per_minute)
        self.updated_at = time.monotonic()
        self.lock = asyncio.Lock() # ใช้ Lock เพื่อรองรับการทำงานแบบ Concurrency ใน FastAPI ((12)) ((29))

    async def check_limit(self):
        """
        ตรวจสอบและหักลบจำนวน Token สำหรับคำขอปัจจุบัน ((17)).
        หาก Token หมด ระบบจะทำการหน่วงเวลา (Throttling) หรือยกเลิกคำขอตามความเหมาะสม ((1)) ((8)).
        """
        async with self.lock:
            self._add_new_tokens()
            
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                logger.debug(f"Rate Limit Check: Passed (Remaining Tokens: {int(self.tokens)})")
                return True
            
            # กรณี Token หมด สามารถเลือกที่จะรอ (Wait) หรือปฏิเสธคำขอทันที ((9)) ((33))
            logger.warning(f"Rate Limit Exceeded: API quota for {settings.WEATHER_API_BASE_URL} is reached")
            raise RateLimitExceeded("API quota limit reached. Please try again later.")

    def _add_new_tokens(self):
        """เติม Token ลงใน Bucket ตามเวลาที่ผ่านไป (Token Bucket Algorithm) ((17))"""
        now = time.monotonic()
        time_passed = now - self.updated_at
        
        # คำนวณจำนวน Token ใหม่ที่ควรได้รับตามอัตราส่วนต่อวินาที ((9))
        new_tokens = time_passed * (self.rate_limit_per_minute / 60.0)
        
        if new_tokens > 0:
            self.tokens = min(float(self.rate_limit_per_minute), self.tokens + new_tokens)
            self.updated_at = now

    async def wait_for_slot(self, timeout: float = 5.0):
        """
        ฟังก์ชัน Throttling ที่จะรอจนกว่าจะมี Slot ว่างสำหรับส่งคำขอ ((1)) ((20)).
        มีระบบ Timeout เพื่อป้องกันไม่ให้ Request ของผู้ใช้งานรอนานเกินไป ((33)).
        """
        start_time = time.monotonic()
        while True:
            try:
                await self.check_limit()
                return
            except RateLimitExceeded:
                if time.monotonic() - start_time > timeout:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Server is busy due to high weather data demand"
                    )
                # หน่วงเวลาสั้นๆ ก่อนตรวจสอบอีกครั้งเพื่อลดภาระของ CPU ((12))
                await asyncio.sleep(0.5)
```

การนำระบบ Rate Limiting มาใช้งานภายใน FastAPI boilerplate{{2}} มีความสำคัญอย่างยิ่งสำหรับการสร้างแอปพลิเคชันระดับองค์กรที่ต้องพึ่งพาข้อมูลจากภายนอกอย่างต่อเนื่อง ((6)) ((16)). ในระดับการออกแบบ ตัวจัดการนี้ถูกสร้างขึ้นเพื่อรองรับโครงสร้างการทำงานแบบไม่ปิดกั้น (Non-blocking) โดยการใช้ `asyncio.Lock` เพื่อให้แน่ใจว่าการตรวจสอบจำนวน Token ในสภาวะที่มีการเข้าถึงข้อมูลพร้อมกัน (High Concurrency) จะมีความแม่นยำและไม่เกิดปัญหา Race Condition ((12)) ((29)). การใช้เทคนิค Token Bucket ช่วยให้ระบบมีความยืดหยุ่น โดยสามารถรองรับคำขอที่เป็นกลุ่มก้อน (Burst Traffic) ได้ในช่วงเวลาสั้นๆ ตราบใดที่จำนวน Token รวมยังไม่เกินขีดจำกัดสูงสุดที่ตั้งไว้ ((17)) ((30)).

เพื่อให้สอดคล้องกับแนวทางปฏิบัติที่ดีที่สุด (Best Practices) ของ The Weather Company ระบบควรมีการระบุสถานะของการจัดการคำขออย่างชัดเจน ((8)) ((9)). เมื่อแอปพลิเคชันตรวจพบว่ามีการเรียกใช้งานเกินโควตา ตัว Rate Limiter จะทำการส่งสัญญาณผ่าน `RateLimitExceeded` Exception ซึ่งชั้น Service หรือ Router สามารถนำไปประมวลผลต่อเพื่อแสดงข้อความที่เหมาะสมแก่ผู้ใช้งาน หรือเลือกที่จะดึงข้อมูลสำรองจาก Cache มาแสดงผลแทน (Fallback mechanism) เพื่อรักษาคุณภาพการให้บริการ ((9)) ((17)) ((33)). การทำ Throttling หรือการหน่วงเวลาคำขอไว้ชั่วคราวผ่านฟังก์ชัน `wait_for_slot` เป็นอีกหนึ่งวิธีที่ช่วยรักษาอัตราการสำเร็จของคำขอ (Success Rate) ในช่วงที่มีการใช้งานหนาแน่น โดยไม่ต้องปฏิเสธคำขอในทันที ((1)) ((20)).

นอกจากนี้ การออกแบบให้ระบบ Rate Limiting ทำงานร่วมกับไฟล์ตั้งค่าใน `app/config/weather_settings.py` ช่วยให้ผู้ดูแลระบบสามารถปรับเปลี่ยนพารามิเตอร์ต่างๆ เช่น จำนวนคำขอสูงสุดต่อนาที ได้ทันทีผ่าน Environment Variables โดยไม่ต้องแก้ไขตัวโค้ดหลัก ((33)). ความสามารถในการปรับแต่งได้นี้มีความสำคัญมากเมื่อมีการอัปเกรดแผนการใช้งาน API ขององค์กร หรือเมื่อต้องการจำกัดปริมาณการใช้งานในสภาพแวดล้อมสำหรับการทดสอบ (Staging Environment) เพื่อควบคุมต้นทุนอย่างมีประสิทธิภาพ ((16)) ((21)).

การตรวจสอบสถานะผ่านระบบ Logging ที่มีการระบุรายละเอียดของสถานะ Token ที่เหลืออยู่ จะช่วยให้ทีมพัฒนาสามารถวิเคราะห์รูปแบบการใช้งานและวางแผนการขยายระบบในอนาคตได้อย่างแม่นยำ ((6)) ((20)). ข้อมูลเหล่านี้ยังสามารถนำไปใช้ในการแจ้งเตือน (Monitoring Alert) เมื่อปริมาณการใช้งานเริ่มเข้าใกล้ขีดจำกัดสูงสุด เพื่อให้ทีมงานเตรียมพร้อมสำหรับการจัดการทรัพยากรได้อย่างทันท่วงที ((9)) ((33)). ทั้งหมดนี้คือส่วนประกอบที่ทำให้ระบบภูมิอากาศใน FastAPI{{7}} ของคุณมีความเป็นมืออาชีพและทนทานต่อสภาวะการใช้งานจริงในระยะยาว ((1)) ((16)) ((29)).

หัวข้อที่คุณอาจอยากดูต่อ:
- Ratelimitprotection: กลยุทธ์การออกแบบระบบป้องกันการเรียกใช้งาน API เกินโควตา
- Token Bucket Algorithm: เจาะลึกอัลกอริทึมยอดนิยมสำหรับการทำ Traffic Shaping
- FastAPI Dependency Injection: การนำ Rate Limiter ไปใช้งานเป็น Dependency ใน Router
- API Cost Management: เทคนิคการลดต้นทุนการใช้งาน Weather Data ผ่านระบบ Throttling
