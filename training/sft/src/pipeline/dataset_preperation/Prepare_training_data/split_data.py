from src.utils.CONFIG import CONFIG
from sklearn.model_selection import train_test_split
import pandas as pd


def split_train_test(
    input_csv,
    train_output,
    test_output,
    test_size=0.2,
    random_state=42
):
    """
    Split dataset menjadi train dan test.
    Default ratio = 80:20
    """

    # Load CSV
    df = pd.read_csv(input_csv)

    # Split data
    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        shuffle=True,
        random_state=random_state
    )

    # Save output
    train_df.to_csv(train_output, index=False)
    test_df.to_csv(test_output, index=False)

    print(f"Train saved: {train_output}")
    print(f"Test saved : {test_output}")
    print(f"Train size : {len(train_df)}")
    print(f"Test size  : {len(test_df)}")