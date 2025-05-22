import django_filters

from .models import Volatile


class VolatileFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    kind = django_filters.CharFilter(field_name="kind", lookup_expr="iexact")
    availability = django_filters.BooleanFilter(field_name="availability")
    start_date = django_filters.DateTimeFilter(
        field_name="timestamp", lookup_expr="gte"
    )
    end_date = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr="lte")

    class Meta:
        model = Volatile
        fields = [
            "kind",
            "availability",
            "min_price",
            "max_price",
            "start_date",
            "end_date",
        ]
