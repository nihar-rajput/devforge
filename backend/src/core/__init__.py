"""
Core domain layer.

This package contains the pure domain model: entities, value objects,
enumerations, events, abstract ports, and error types.

CRITICAL RULE: Nothing in this package may import from infrastructure,
API, or framework layers. This is the innermost ring of clean architecture.
"""
