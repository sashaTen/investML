from django.urls import path
from .views import index,  predict ,  dashboard , sign_up ,   create_portfolio , portfolio_list , choose_tickers , delete_ticker , delete_portfolio, get_prediction

urlpatterns = [
    path("", index, name="index"),
    path("dashboard/", dashboard, name="dashboard"),
    path("sign_up/", sign_up, name="sign_up"),
    path("create_portfolio/", create_portfolio, name="create_portfolio"),
    path("portfolio_list/", portfolio_list, name="portfolio_list"),
    path("choose_tickers/", choose_tickers, name="choose_tickers"),
    path("predict/", predict, name="predict"),
    path("delete_ticker/<int:ticker_id>/", delete_ticker, name="delete_ticker"),
    path("delete_portfolio/<int:portfolio_id>/", delete_portfolio, name="delete_portfolio"),
    path("get_prediction/<str:ticker_id>/", get_prediction, name="get_prediction"),
]
