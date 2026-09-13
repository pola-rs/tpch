from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from queries.pandas import utils

if TYPE_CHECKING:
    import pandas as pd

Q_NUM = 5


def q() -> None:
    region_ds_fn = utils.get_region_ds
    nation_ds_fn = utils.get_nation_ds
    customer_ds_fn = utils.get_customer_ds
    line_item_ds_fn = utils.get_line_item_ds
    orders_ds_fn = utils.get_orders_ds
    supplier_ds_fn = utils.get_supplier_ds

    # first call one time to cache in case we don't include the IO times
    region_ds_fn()
    nation_ds_fn()
    customer_ds_fn()
    line_item_ds_fn()
    orders_ds_fn()
    supplier_ds_fn()

    def query() -> pd.DataFrame:
        region_ds = region_ds_fn()
        nation_ds = nation_ds_fn()
        customer_ds = customer_ds_fn()
        line_item_ds = line_item_ds_fn()
        orders_ds = orders_ds_fn()
        supplier_ds = supplier_ds_fn()

        var1 = "ASIA"
        var2 = date(1994, 1, 1)
        var3 = date(1995, 1, 1)

        region_ds = region_ds[region_ds["r_name"] == var1]
        orders_ds = orders_ds[
            (orders_ds["o_orderdate"] >= var2) & (orders_ds["o_orderdate"] < var3)
        ]

        jn1 = region_ds.merge(nation_ds, left_on="r_regionkey", right_on="n_regionkey")
        jn2 = jn1.merge(customer_ds, left_on="n_nationkey", right_on="c_nationkey")
        jn3 = jn2.merge(orders_ds, left_on="c_custkey", right_on="o_custkey")
        jn4 = jn3.merge(line_item_ds, left_on="o_orderkey", right_on="l_orderkey")
        jn5 = jn4.merge(
            supplier_ds,
            left_on=["l_suppkey", "n_nationkey"],
            right_on=["s_suppkey", "s_nationkey"],
        )

        jn5["revenue"] = jn5.l_extendedprice * (1.0 - jn5.l_discount)

        gb = jn5.groupby("n_name", as_index=False)["revenue"].sum()
        result_df = gb.sort_values("revenue", ascending=False)

        return result_df  # type: ignore[no-any-return]

    utils.run_query(Q_NUM, query)


if __name__ == "__main__":
    q()
