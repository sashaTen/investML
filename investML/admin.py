
from django.contrib import admin
from .models import Tickers ,  Portfolio , RiskToleranceProfile

admin.site.register(Tickers )
admin.site.register(Portfolio)
admin.site.register(RiskToleranceProfile)