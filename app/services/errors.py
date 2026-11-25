class NotFoundError(Exception):
    """La entidad solicitada no existe."""


class ConflictError(Exception):
    """La operación incumple una regla de unicidad."""
