#     pytest  -m   unit
from investML.miscelan import print_any 
from  ml_code.testing_ml  import load_df
import pytest
import pandas as pd



@pytest.mark.unit
def test_print_any():

    test_word = "Hello, InvestML!"
    print_any(test_word)  # Just ensure it runs without error
    assert True  # If no exception, the test passes




def test_load_df(tmp_path):
    # create fake csv
    csv_file = tmp_path / "fake.csv"
    csv_file.write_text("a,b\n1,2\n3,4")

    df = load_df(csv_file)

    assert not df.empty
    assert list(df.columns) == ["a", "b"]

