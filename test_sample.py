
from  ml_code.testing_ml  import load_df
import pytest
import pandas as pd







def test_load_df(tmp_path):
    # create fake csv
    csv_file = tmp_path / "fake.csv"
    csv_file.write_text("a,b\n1,2\n3,4")

    df = load_df(csv_file)

    assert not df.empty
    assert list(df.columns) == ["a", "b"]

