"""
Abstract port interfaces (ABCs).

These define the boundaries between the domain and infrastructure.
Concrete implementations (SQLite, Windows Registry, etc.) live
in the infrastructure layer and are injected via dependency injection.
"""
