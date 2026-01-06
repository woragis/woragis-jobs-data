# Changelog

## [Unreleased]

### Added
- CI/CD workflows following ai-service pattern
  - Unit tests with coverage reporting
  - Integration tests with PostgreSQL and Redis services
  - Docker build validation
  - Security scanning (Bandit, Safety, pip-audit)
  - Codecov integration
- Integration with jobs service
  - JobsServiceClient for fetching applications
  - Real-time recommendation generation from jobs service data
  - Analytics sync with jobs service
- Redis caching
  - Recommendations caching with TTL
  - Company metrics caching
  - User metrics caching
  - Cache invalidation methods
  - Graceful fallback when Redis unavailable
- ML Models implementation
  - Success prediction model (RandomForest Classifier)
  - Response time prediction model (RandomForest Regressor)
  - Model training pipeline
  - Model prediction API endpoints
  - Model metadata storage in database

### Changed
- Recommendations API now fetches real data from jobs service
- Analytics API syncs with jobs service for up-to-date metrics
- Recommendation service uses Redis cache for performance

### Technical Details
- All features committed with proper git messages
- Follows same CI/CD pattern as ai-service
- Tests can run in cloud CI environment
- ML models require minimum 10 applications for training

