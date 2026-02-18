# Changelog

All notable changes to StreamForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Additional exchange integrations
- Enhanced error handling and retry mechanisms
- Comprehensive test suite
- Performance optimizations
- Scheduling for API and Websockets
- Calculation Engine Module

---

## [0.1.3] - 2026-02-18

### Added
- Bybit exchange integration with full support for:
  - Real-time WebSocket streaming (kline/OHLC data)
  - Historical backfilling via REST API
  - Support for multiple market types: Spot, Linear (USDT/USDC perpetuals), and Inverse futures
- BybitBackfilling class for historical data retrieval
- Unified rate limiting for all Bybit market types (shared endpoint)

### Technical Details
- API-only backfilling approach (no CSV downloads available)
- Maximum 1000 candles per API request
- Rate limit: 500 requests per 5 seconds (conservative limit)
- Support for all Bybit timeframes: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 1d, 1w, 1M

### Fixes
- Okx backfilling fix

[0.1.3]: https://github.com/paulobueno90/streamforge/releases/tag/v0.1.3

## [0.1.2] - 2026-02-04
- Added Binance futures support (klines)
- Small fixes for okx
- Fix on duplicated log
- Small changes in examples

[0.1.2]: https://github.com/paulobueno90/streamforge/releases/tag/v0.1.2

## [0.1.1] - 2026-01-20

### Fixed
- Backfilling for binance failing when a transformer was not set.
- Added standard behavior, now it backfills correctly from CSV

[0.1.1]: https://github.com/paulobueno90/streamforge/releases/tag/v0.1.1

## [0.1.0] - 2025-01-06

### Added
- Initial release of StreamForge
- Real-time WebSocket data ingestion from multiple exchanges:
  - Binance integration with kline/OHLC support
  - Kraken integration with OHLC support
  - OKX integration with candlestick support
- Multiple data output formats:
  - CSV file output
  - PostgreSQL database integration
  - Kafka streaming support
- Data processing features:
  - OHLC/Kline data normalization
  - Timeframe aggregation
  - Data buffering and processing
- Base framework for exchange integrations:
  - Abstract base classes for WebSocket handlers
  - Data processor architecture
  - Emitter pattern for output handling
  - Stream input configuration
- Cross-platform compatibility (Windows, Linux, macOS)
- Async/await architecture for high performance
- Type hints and Pydantic models for data validation

### Infrastructure
- Modern Python packaging with pyproject.toml
- Comprehensive .gitignore
- MIT License
- Professional README and documentation
- Installation guide

---

## Links

- [Unreleased]: https://github.com/paulobueno90/streamforge/compare/v0.1.3...HEAD
- [0.1.3]: https://github.com/paulobueno90/streamforge/compare/v0.1.2...v0.1.3
- [0.1.2]: https://github.com/paulobueno90/streamforge/compare/v0.1.1...v0.1.2
- [0.1.1]: https://github.com/paulobueno90/streamforge/compare/v0.1.0...v0.1.1
- [0.1.0]: https://github.com/paulobueno90/streamforge/releases/tag/v0.1.0

