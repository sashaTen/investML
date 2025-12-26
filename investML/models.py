from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings




class Tickers(models.Model):
    ticker = models.CharField(max_length=100)
    prediction = models.FloatField(default=0.0)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickers",default=None
    )

    def __str__(self):
        return self.ticker




""" class   Portfolio(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portfolios"
    )
    name = models.CharField(max_length=100)
    total_budget = models.FloatField(default=0)
    risk_tolerance = models.FloatField(default=0.5)
    tickers =  models.ManyToManyField(Tickers, related_name='portfolios')
    MAX_TICKERS = 10

    def clean(self):
        if self.pk and self.tickers.count() > self.MAX_TICKERS:
            raise ValidationError("A portfolio can contain at most 10 tickers.")

    def __str__(self):
        return self.name """




class  Portfolio(models.Model):
    STABILITY_CHOICES = [
        (1, "Very unstable"),
        (2, "Unstable"),
        (3, "Average"),
        (4, "Stable"),
        (5, "Very stable"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="portfolios"
    )

    time_horizon_years = models.PositiveIntegerField(
        help_text="How many years until you need this money"
    )

    salary_stability = models.IntegerField(
        choices=STABILITY_CHOICES
    )

    average_monthly_income = models.FloatField(default=0)


    investment_percentage = models.FloatField(
        help_text="Percentage of savings to invest (0–100)"
    )

    investing_experience_years = models.IntegerField(
        help_text="Years of investing experience (0–4)"
    )

   

    
    tickers =  models.ManyToManyField(Tickers, related_name='portfolios')

    def __str__(self):
        return f"{self.user.username} Risk Profile"
    MAX_TICKERS = 10

    def clean(self):
        if self.pk and self.tickers.count() > self.MAX_TICKERS:
            raise ValidationError("A portfolio can contain at most 10 tickers.")

    






