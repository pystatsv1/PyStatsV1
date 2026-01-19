"""Exceptions for Track D helpers."""

from __future__ import annotations


class TrackDError(Exception):
    """Base exception for Track D helpers."""


class TrackDDataError(TrackDError):
    """Raised when Track D input data is missing or invalid."""


class TrackDSchemaError(TrackDError):
    """Raised when Track D input data fails schema/contract checks."""
