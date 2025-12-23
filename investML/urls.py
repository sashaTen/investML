from django.urls import path
from .views import index,  predict ,  dashboard , sign_up ,   create_portfolio , portfolio_list , choose_tickers

urlpatterns = [
    path("", index, name="index"),
    path("dashboard/", dashboard, name="dashboard"),
    path("sign_up/", sign_up, name="sign_up"),
    path("create_portfolio/", create_portfolio, name="create_portfolio"),
    path("portfolio_list/", portfolio_list, name="portfolio_list"),
    path("choose_tickers/", choose_tickers, name="choose_tickers"),
    path("predict/", predict, name="predict"),
]
