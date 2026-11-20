import pandas as pd

DATASET_PATH = "data/dataset_parte2/soc-redditHyperlinks-body.tsv"

df = pd.read_csv(
    DATASET_PATH,
    sep="\t",
)

print("Shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())

print("\nTypes:")
print(df.dtypes)

print("\nFirst rows:")
print(df.head())

print("\nMissing values:")
print(df.isna().sum())

print("\nExact duplicate rows:")
print(df.duplicated().sum())

print("\nUnique source subreddits:")
print(df["SOURCE_SUBREDDIT"].nunique())

print("\nUnique target subreddits:")
print(df["TARGET_SUBREDDIT"].nunique())

all_subreddits = (
    set(df["SOURCE_SUBREDDIT"])
    | set(df["TARGET_SUBREDDIT"])
)

print("\nTotal unique subreddits:")
print(len(all_subreddits))

print("\nLINK_SENTIMENT distribution:")
print(
    df["LINK_SENTIMENT"]
    .value_counts(dropna=False)
)

print("\nLINK_SENTIMENT unique values:")
print(
    sorted(
        df["LINK_SENTIMENT"]
        .dropna()
        .unique()
    )
)

print("\nNegative interactions:")
print(
    (df["LINK_SENTIMENT"] == -1).sum()
)

print("\nPositive interactions:")
print(
    (df["LINK_SENTIMENT"] == 1).sum()
)

print("\nUnique post IDs:")
print(df["POST_ID"].nunique())

print("\nDuplicated POST_IDs:")
print(
    df["POST_ID"]
    .duplicated()
    .sum()
)

pair_counts = (
    df.groupby([
        "SOURCE_SUBREDDIT",
        "TARGET_SUBREDDIT",
    ])
    .size()
    .sort_values(ascending=False)
)

print("\nRepeated source-target pairs:")
print(
    (pair_counts > 1).sum()
)

print("\nMost repeated source-target pairs:")
print(
    pair_counts.head(20)
)

print("\nSelf-links:")
print(
    (
        df["SOURCE_SUBREDDIT"]
        == df["TARGET_SUBREDDIT"]
    ).sum()
)

df["TIMESTAMP_PARSED"] = pd.to_datetime(
    df["TIMESTAMP"],
    errors="coerce",
)

print("\nInvalid timestamps:")
print(
    df["TIMESTAMP_PARSED"]
    .isna()
    .sum()
)

print("\nTimestamp range:")
print(
    df["TIMESTAMP_PARSED"].min()
)
print(
    df["TIMESTAMP_PARSED"].max()
)

print("\nUnique directed source-target pairs:")
print(len(pair_counts))

repeated_rows = pair_counts[pair_counts > 1]

print("\nNumber of interactions represented by repeated pairs:")
print(repeated_rows.sum())

print("\nMaximum multiplicity:")
print(pair_counts.max())

pair_sentiments = (
    df.groupby([
        "SOURCE_SUBREDDIT",
        "TARGET_SUBREDDIT",
    ])["LINK_SENTIMENT"]
    .nunique()
)

print("\nPairs with both positive and negative interactions:")
print((pair_sentiments > 1).sum())
