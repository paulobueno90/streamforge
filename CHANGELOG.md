# Changelog

All notable changes to StreamForge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Additional exchange integrations
- Enhanced error handling and retry mechanisms
- Comprehensive test suite
- Performance optimizations

## [0.1.1] - 2026-01-20

### Fixed
- Backfilling for binance failing when a transformer was not set.
- Added standard behavior, now it backfills correctly from CSV

[0.1.1]: https://github.com/paulobueno90/streamforge/releases/tag/v0.1.1

## [0.1.0] - 2025-10-14

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
  - Logger output
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

[Unreleased]: https://github.com/paulobueno90/streamforge/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/paulobueno90/streamforge/releases/tag/v0.1.0
