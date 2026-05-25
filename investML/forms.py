from django import forms
from .models import Portfolio ,  Tickers , RiskToleranceProfile
""" class PortfolioCreateForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ["name", "total_budget", "risk_tolerance" ] """





class PortfolioCreateForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = [
            "time_horizon_years",
            'budget',
            "salary_stability",
            "average_monthly_income",
            "investment_percentage",
            "investing_experience_years",
           
        ]

        widgets = {
            "time_horizon_years": forms.NumberInput(attrs={"class": "input"}),
            'budget': forms.NumberInput(attrs={"class": "input"}),
            "salary_stability": forms.Select(attrs={"class": "input"}),
            "average_monthly_income": forms.NumberInput(attrs={"class": "input"}),
            "investment_percentage": forms.NumberInput(attrs={"class": "input"}),
            "investing_experience_years": forms.NumberInput(attrs={"class": "input"}),
          
        }




class TickerForm(forms.ModelForm):
    class Meta:
        model = Tickers
        fields = ["ticker", "prediction"]





class RiskToleranceForm(forms.ModelForm):
    class Meta:
        model = RiskToleranceProfile
        # Exclude relational and automated fields so the user cannot manipulate them
        exclude = ['user', 'calculated_score', 'assigned_profile']
        
        # Swap out default dropdown select fields for clean, scannable radio options
        widgets = {
            'time_horizon_years': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 10',
                'min': '1'
            }),
            'emergency_fund_months': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'portfolio_net_worth_ratio': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'hypothetical_drawdown_reaction': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'past_behavior_2022': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'tradeoff_preference': forms.RadioSelect(attrs={'class': 'form-check-input'}),
        }
        
        # User-friendly descriptive labels to override database technical names
        labels = {
            'time_horizon_years': 'Investment Time Horizon',
            'emergency_fund_months': 'Emergency Fund Size',
            'portfolio_net_worth_ratio': 'Portfolio Concentration Weight',
            'hypothetical_drawdown_reaction': 'Reaction to Sudden Market Crashes',
            'past_behavior_2022': 'Your Past Bear Market Activity',
            'tradeoff_preference': 'Risk vs. Reward Strategy Preference',
        }

    def __init__(self, *for_user, **kwargs):
        super().__init__(*for_user, **kwargs)
        # Optional: Apply modern form control wrapper classes to all choice fields dynamically
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.update({'class': 'form-control'})
