#     pytest  -m   unit
from investML.miscelan import print_any 
from  ml_code.testing_ml  import load_df
import pytest
import pandas as pd
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = BASE_DIR / "ml_artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)
path = ARTIFACTS_DIR / "stock_data.csv"


@pytest.mark.unit
def test_print_any():

    test_word = "Hello, InvestML!"
    print_any(test_word)  # Just ensure it runs without error
    assert True  # If no exception, the test passes




def  test_load_df():
    df = load_df("C:\\Users\\HP\\Desktop\\investML\\ml_code\\stock_data.csv")
    assert df is not None
    assert not df.empty 

