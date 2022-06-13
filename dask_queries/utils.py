from os.path import join
from typing import Callable, Union

import dask.dataframe as dd
import pandas as pd
import polars as pl
from linetimer import CodeTimer, linetimer

from utils import (
    INCLUDE_IO,
    __default_answers_base_dir,
    __default_dataset_base_dir,
    on_second_call,
)


def __read_parquet_ds(path: str) -> Union:
    if INCLUDE_IO:
        return dd.read_parquet(path)
    return dd.from_pandas(pl.read_parquet(path).to_pandas(), npartitions=12)


def get_query_answer(
    query: int, base_dir: str = __default_answers_base_dir
) -> dd.DataFrame:
    answer_df = pd.read_csv(
        join(base_dir, f"q{query}.out"),
        sep="|",
        parse_dates=True,
        infer_datetime_format=True,
    )
    return answer_df.rename(columns=lambda x: x.strip())


def test_results(q_num: int, result_df: pd.DataFrame):
    with CodeTimer(name=f"Testing result of Query {q_num}", unit="s"):
        answer = get_query_answer(q_num)

        for c, t in answer.dtypes.items():
            s1 = result_df[c]
            s2 = answer[c]

            if t.name == "object":
                s1 = s1.astype("string").apply(lambda x: x.strip())
                s2 = s2.astype("string").apply(lambda x: x.strip())

            pd.testing.assert_series_equal(left=s1, right=s2, check_index=False)


@on_second_call
def get_line_item_ds(base_dir: str = __default_dataset_base_dir) -> dd.DataFrame:
    return __read_parquet_ds(join(base_dir, "lineitem.parquet"))


@on_second_call
def get_orders_ds(base_dir: str = __default_dataset_base_dir) -> dd.DataFrame:
    return __read_parquet_ds(join(base_dir, "orders.parquet"))


@on_second_call
def get_customer_ds(base_dir: str = __default_dataset_base_dir) -> dd.DataFrame:
    return __read_parquet_ds(join(base_dir, "customer.parquet"))


@on_second_call
def get_region_ds(base_dir: str = __default_dataset_base_dir) -> dd.DataFrame:
    return __read_parquet_ds(join(base_dir, "region.parquet"))


@on_second_call
def get_nation_ds(base_dir: str = __default_dataset_base_dir) -> dd.DataFrame:
    return __read_parquet_ds(join(base_dir, "nation.parquet"))


@on_second_call
def get_supplier_ds(base_dir: str = __default_dataset_base_dir) -> dd.DataFrame:
    return __read_parquet_ds(join(base_dir, "supplier.parquet"))


@on_second_call
def get_part_ds(base_dir: str = __default_dataset_base_dir) -> dd.DataFrame:
    return __read_parquet_ds(join(base_dir, "part.parquet"))


@on_second_call
def get_part_supp_ds(base_dir: str = __default_dataset_base_dir) -> dd.DataFrame:
    return __read_parquet_ds(join(base_dir, "partsupp.parquet"))


def run_query(q_num: str, query: Callable):
    @linetimer(name=f"Overall execution of Query {q_num}", unit="s")
    def run():
        with CodeTimer(name=f"Get result of Query {q_num}", unit="s"):
            result = query()

        print(result)
        test_results(q_num, result)

    run()