from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings




class Tickers(models.Model):
    ticker = models.CharField(max_length=100)
    prediction = models.FloatField(default=42.0)
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
    budget = models.FloatField(default=0)

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

    risk =   models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} Risk Profile"
    MAX_TICKERS = 10

    def clean(self):
        if self.pk and self.tickers.count() > self.MAX_TICKERS:
            raise ValidationError("A portfolio can contain at most 10 tickers.")
        
    def calculate_risk_score(self):
        score = 0

        # Time horizon
        if self.time_horizon_years >= 4:
            score += 35
        elif self.time_horizon_years >= 1:
            score += 25
        else:
            score += 15

        # Salary stability (1–5)
        score += self.salary_stability * 5

        # Investment percentage
        if self.investment_percentage >= 50:
            score += 25
        elif self.investment_percentage >= 30:
            score += 15
        else:
            score += 5

        # Experience (0–4)
        score += self.investing_experience_years * 5

        return min(score, 100)

    def risk_tolerance(self):
        score = self.calculate_risk_score()

        if score < 35:
            return 1
        elif score < 65:
            return 2
        else:
            return 3

    def save(self, *args, **kwargs):
        self.risk = self.calculate_risk_score()
        super().save(*args, **kwargs)






class  Sentiment(models.Model):
    ticker = models.CharField(max_length=100)
    sentiment_text = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.ticker} -  on {self.date}"
    




from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class RiskToleranceProfile(models.Model):
    """
    Stores and calculates the risk tolerance profile of a client 
    specifically optimized for a stock-only portfolio.
    """
    
    RISK_PROFILES = [
        ('CONSERVATIVE', 'Conservative Equity (Low Volatility / Dividend Focus)'),
        ('MODERATE', 'Moderate Equity (Core Broad-Market / Balanced Sectors)'),
        ('AGGRESSIVE', 'Aggressive Equity (Growth Focus / High Beta)'),
        ('SPECULATIVE', 'Hyper-Aggressive / Speculative Equity (Concentrated / Small-Cap)'),
    ]

    # 1. Relational Link
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='risk_profile'
    )
    
    # 2. HARD CAPACITY METRICS (The Math)
    time_horizon_years = models.PositiveIntegerField(
        help_text="In how many years do you plan to begin withdrawing major funds from this portfolio?",
        validators=[MinValueValidator(1)]
    )
        
    emergency_fund_months = models.IntegerField(
        help_text="How many months of living expenses are covered by cash/liquid assets outside of this stock portfolio?",
        choices=[
            (0, "0 to 2 months"),
            (1, "3 to 6 months"),
            (2, "6+ months")
        ]
    )
    
    portfolio_net_worth_ratio = models.IntegerField(
        help_text="What percentage of your total liquid net worth does this investment represent?",
        choices=[
            (3, "Less than 25%"),
            (2, "25% to 50%"),
            (1, "More than 50%")
        ]
    )

    # 3. BEHAVIORAL ATTITUDE METRICS (The Psychology)
    MARKET_REACTION_CHOICES = [
        (0, "Panic: I would sell everything to cash immediately to prevent further loss."),
        (1, "Anxious: I would freeze, do nothing, but lose sleep over it."),
        (2, "Patient: I would hold tight, knowing the equity market moves in cycles."),
        (3, "Opportunistic: I would treat it as a discount sale and buy more shares."),
    ]
    hypothetical_drawdown_reaction = models.IntegerField(
        help_text="If your equity portfolio drops 25% in one month, what is your most likely reaction?",
        choices=MARKET_REACTION_CHOICES
    )
    
    past_behavior_2022 = models.IntegerField(        help_text="During the last major market correction (e.g., 2022 bear market), how did you handle your investments?",
        choices=[
            (0, "I didn't own stocks then / I panic-sold my positions."),
            (1, "I held onto my stocks but felt highly uncomfortable."),
            (2, "I systematically held and rebalanced, or added capital."),
        ]
    )
    
    tradeoff_preference = models.IntegerField(
        help_text="Which investment profile makes you more comfortable?",
        choices=[
            (1, "Low volatility, predictable returns, minimal chance of massive single-year drops."),
            (2, "Average volatility, mimics the broader S&P 500 benchmark performance."),
            (3, "High volatility, chasing significant outperformance with the risk of multi-year downturns."),
        ]
    )

    # 4. AUTOMATION METADATA
    calculated_score = models.IntegerField(blank=True, null=True, editable=False)
    assigned_profile = models.CharField(
        max_length=20, 
        choices=RISK_PROFILES, 
        blank=True, 
        editable=False
    )
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_risk_profile(self):
        """
        Business logic to score the client and assign a definitive 
        stock-only portfolio risk tier.
        """
        score = 0
               
        # Horizon scoring (Critical for pure stock portfolios)
        if self.time_horizon_years <= 3:
            score += 0   # Short horizon severely restricts stock capacity
        elif self.time_horizon_years <= 7:
            score += 2
        else:
            score += 5   # Long horizons allow high equity risk absorption
            
        # Add up choice values acting as points
        score += self.emergency_fund_months
        score += self.portfolio_net_worth_ratio
        score += self.hypothetical_drawdown_reaction
        score += self.past_behavior_2022
        score += self.tradeoff_preference
        
        self.calculated_score = score
        
        # Hard constraint override: If time horizon is less than 3 years, 
        # force a maximum of CONSERVATIVE regardless of psychological bravery.
        if self.time_horizon_years < 3:
            self.assigned_profile = 'CONSERVATIVE'
        else:
            if score <= 5:
                self.assigned_profile = 'CONSERVATIVE'
            elif score <= 10:
                self.assigned_profile = 'MODERATE'
            elif score <= 15:
                self.assigned_profile = 'AGGRESSIVE'
            else:
                self.assigned_profile = 'SPECULATIVE'
                
        return self.assigned_profile


    def save(self, *args, **kwargs):
        # Automatically compute engine scores before database insertion
        self.calculate_risk_profile()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.assigned_profile} ({self.calculated_score} pts)"
