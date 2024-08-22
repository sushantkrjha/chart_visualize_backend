
from django.urls import path
from .views import (
    TotalSalesOverTime,
    SalesGrowthRateOverTime,
    NewCustomersAddedOverTime,
    RepeatCustomersCount,
    GeographicalDistribution,
    CustomerLifetimeValueByCohorts
)

urlpatterns = [
    path('total-sales/<str:interval>/', TotalSalesOverTime.as_view(), name='total_sales'),
    path('sales-growth/', SalesGrowthRateOverTime.as_view(), name='sales_growth'),
    path('new-customers/<str:interval>/', NewCustomersAddedOverTime.as_view(), name='new_customers'),
    path('repeat-customers/', RepeatCustomersCount.as_view(), name='repeat_customers'),
    path('geographical-distribution/', GeographicalDistribution.as_view(), name='geo_distribution'),
    path('customer-lifetime-value/', CustomerLifetimeValueByCohorts.as_view(), name='customer_lifetime_value')
]