from django import forms
from .models import Portfolio

class PortfolioCreateForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ["name", "total_budget", "risk_tolerance"]



