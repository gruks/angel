# Technology Stack

**Project:** ConflictPulse - Real-Time Conflict Prediction Platform  
**Researched:** 2026-03-27  
**Confidence:** HIGH

## Recommended Stack

### Core API Framework
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| FastAPI | 0.135.x | REST API + WebSocket server | Industry-standard Python async framework; WebSocket support via Starlette is production-ready; 0.135.x (March 2026) is current stable with Pydantic v2.9+ support. WebSocket pattern: use `WebSocketDisconnect` exception handling and connection manager pattern for real-time predictions. |
| Starlette | Latest | Async foundations | Required by FastAPI; handles WebSocket lifecycle, dependency injection |
| Pydantic | 2.9+ | Data validation | Required by FastAPI; models for request/response schemas |

### Database Layer
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| TimescaleDB | 2.26.x | Time-series data (conflict events, predictions) | PostgreSQL extension for hypertables; v2.26.0 (March 2026) includes vectorized aggregation engine (3.5x faster), composite bloom filters (2x faster query performance). Native continuous aggregates for real-time rollups. |
| PostGIS | 3.6.x | Geospatial queries | Works alongside TimescaleDB; v3.6.2 (Feb 2026) supports PostgreSQL 14-18. Essential for spatial queries (within radius, intersections). |
| PostgreSQL | 17.x | Primary database | Required by TimescaleDB and PostGIS; PG 17.x has best performance |
| Amazon S3 | - | Satellite tile storage | Cost-effective for raster data; integrate via boto3 |

### Data Pipeline & Orchestration
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Apache Kafka | 4.x | Real-time event streaming | Industry standard for 12+ source ingestion; v4.2.0 (2026) has improved partitioning and retention. Use Kafka Connect for CDC from external sources. |
| Apache Airflow | 3.x | DAG-based orchestration | Standard for batch ETL; v3.x (2025+) removes Celry, uses Kubernetes executor by default. Use for daily batch ingestion from GDELT/ACLED APIs. |
| Kafka Connect | Latest | Source connectors | Pre-built connectors for JDBC, HTTP, S3 |

### ML/NLP Pipeline
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| XLM-RoBERTa | base/xlarge | Multilingual text NLP | 100 languages pretrained; Hugging Face Transformers integration. Use for social media, news sentiment across multiple languages. Base for latency, XL for accuracy. |
| YOLOv8 | 8.3.x | Object detection (satellite imagery) | Ultralytics v8.3.x (2025) stable; v8.4.0 released Jan 2026 adds YOLO26 models. Use for detecting military equipment, infrastructure damage in satellite images. |
| SAM (Segment Anything) | 3.x | Image segmentation | SAM 3 (Oct 2025) integrated into Ultralytics as `ultralytics.models.sam`; supports text prompts for concept-based segmentation. Use for automated region delineation. |
| Prophet | Latest | Time-series forecasting | Facebook/Meta maintained; easy to decompose trends/seasonality. Good for univariate conflict event forecasting. |
| TensorFlow Temporal Fusion Transformer | Latest | Advanced forecasting | Use when you need multi-horizon, multi-variate forecasting with attention. Better than Prophet for complex causal relationships between indicators. |
| PyTorch | 2.x | Deep learning backend | Required for YOLOv8, SAM, TFT |

### Frontend Visualization
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Mapbox GL JS | 3.x | Base map rendering | Industry standard for web maps; v3.x supports 3D terrain. Use for analyst dashboard base layer. |
| Deck.gl | 9.3.x | WebGL data visualization | Uber/vis.gl maintained; H3HexagonLayer for hexagonal spatial binning. v9.3 in development (March 2026). Use for overlaying prediction heatmaps. |
| React | 18.x | UI framework | Required for deck.gl/react-map-gl integration |
| H3 | Latest | Geospatial indexing | Uber's hexagonal hierarchical spatial index; integrates with deck.gl for conflict density visualization |

### Alert & Notification
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Twilio SendGrid | Latest | Email alerts | Transactional email for UN/NATO analyst notifications; webhook support for bounce/open tracking |
| Twilio API | Latest | SMS alerts | Critical alerts to mobile devices |
| Webhooks | - | Programmatic alerts | Custom integrations with partner systems |

### Infrastructure & DevOps
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Kubernetes | 1.30+ | Container orchestration | Standard for production deployment; use KubeFlow for ML pipeline orchestration |
| Docker | Latest | Containerization | All services containerized |
| Prometheus + Grafana | Latest | Monitoring | Time-series metrics for system health |
| Redis | 7.x | Caching layer | WebSocket connection state, API response caching |

### Supporting Libraries
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `aiokafka` | Latest | Async Kafka client | Python async consumers for real-time processing |
| `sqlalchemy` | 2.x | ORM | Database models, migrations with Alembic |
| `httpx` | Latest | Async HTTP | External API calls (GDELT, ACLED feeds) |
| `python-multipart` | Latest | Form data | File uploads for satellite imagery |
| `python-jose` | Latest | JWT tokens | API authentication |
| `passlib` | Latest | Password hashing | User authentication |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| API Framework | FastAPI | Flask + Flask-SocketIO | FastAPI has native async, type safety, OpenAPI generation. Flask requires async extensions and has more boilerplate. |
| Time-Series DB | TimescaleDB | InfluxDB | TimescaleDB on PostgreSQL gives you PostGIS for free; single database for all data types. InfluxDB would require separate geospatial solution. |
| Geospatial | PostGIS | GeoMesa, MongoDB Geo | PostGIS is most mature, integrates with TimescaleDB, has extensive function library. GeoMesa requires HBase/Cassandra. |
| Orchestration | Airflow | Dagster, Prefect | Airflow has largest ecosystem, most integrations. Dagster better for asset-oriented pipelines but smaller community. |
| Forecasting | Prophet | ARIMA | Prophet handles missing data, seasonality, holidays better than raw ARIMA. For complex multi-variate, use TFT. |
| Map Visualization | Mapbox + Deck.gl | MapLibre GL | Mapbox has better styling, satellite imagery integration. MapLibre is open-source alternative but requires more custom work for complex viz. |

## Not Recommended

| Technology | Why Not | What to Use Instead |
|------------|---------|---------------------|
| Celery | Additional broker required (Redis/RabbitMQ); Airflow handles batch better | Apache Airflow for batch, Kafka for real-time |
| Django | Synchronous by default; overkill for API-only service | FastAPI |
| MongoDB | Not needed when you have PostgreSQL + PostGIS + TimescaleDB | PostgreSQL ecosystem |
| GraphQL (Apollo) | Adds complexity; REST + WebSocket sufficient for this use case | FastAPI native REST + WebSocket |
| RabbitMQ | Kafka is more standard for event streaming at scale | Apache Kafka |

## Installation

```bash
# Core API
pip install fastapi[all] uvicorn[standard]

# Database
pip install sqlalchemy psycopg2-binary asyncpg timescaledb

# Kafka + Airflow
pip install aiokafka apache-airflow

# ML/NLP
pip install transformers torch ultralytics prophet tensorflow

# Frontend (handled by package.json)
npm install mapbox-gl deck.gl @deck.gl/react h3 react-map-gl

# Infrastructure
pip install redis prometheus-client
```

## Sources

- **FastAPI**: GitHub releases (0.135.2, March 2026) - HIGH confidence
- **TimescaleDB**: GitHub releases (2.26.0, March 2026) - HIGH confidence
- **PostGIS**: postgis.net (3.6.2, Feb 2026) - HIGH confidence
- **YOLOv8**: Ultralytics GitHub (v8.4.0, Jan 2026) - HIGH confidence
- **SAM 3**: Ultralytics docs (Oct 2025) - HIGH confidence
- **Kafka**: WebSearch confirmed industry standard - MEDIUM confidence
- **Airflow**: WebSearch confirmed best practices - MEDIUM confidence
- **Deck.gl**: deck.gl docs (v9.3 in development) - HIGH confidence

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| API Framework | HIGH | FastAPI 0.135.x current stable; verified March 2026 |
| Database | HIGH | TimescaleDB 2.26.0, PostGIS 3.6.2 both confirmed March 2026 |
| ML Pipeline | HIGH | YOLOv8/SAM confirmed via Ultralytics releases; Transformers for XLM-R |
| Frontend | HIGH | Mapbox GL, Deck.gl, H3 all verified via docs |
| Infrastructure | MEDIUM | Standard K8s/Docker patterns confirmed via web search |
| Alerting | HIGH | Twilio/SendGrid well-documented APIs |
