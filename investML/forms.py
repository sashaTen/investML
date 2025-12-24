from django import forms
from .models import Portfolio ,  Tickers
class PortfolioCreateForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ["name", "total_budget", "risk_tolerance" ]






class TickerForm(forms.ModelForm):
    class Meta:
        model = Tickers
        fields = ["ticker", "prediction"]
