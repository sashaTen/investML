from django import forms
from .models import Portfolio ,  Tickers
""" class PortfolioCreateForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ["name", "total_budget", "risk_tolerance" ] """





class PortfolioCreateForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = [
            "time_horizon_years",
            "salary_stability",
            "average_monthly_income",
            "investment_percentage",
            "investing_experience_years",
           
        ]

        widgets = {
            "time_horizon_years": forms.NumberInput(attrs={"class": "input"}),
            "salary_stability": forms.Select(attrs={"class": "input"}),
            "average_monthly_income": forms.NumberInput(attrs={"class": "input"}),
            "investment_percentage": forms.NumberInput(attrs={"class": "input"}),
            "investing_experience_years": forms.NumberInput(attrs={"class": "input"}),
          
        }




class TickerForm(forms.ModelForm):
    class Meta:
        model = Tickers
        fields = ["ticker", "prediction"]
