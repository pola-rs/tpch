from __future__ import annotations

from datetime import date

import pandas as pd

from queries.pandas import utils

Q_NUM = 4


def q() -> None:
    line_item_ds_fn = utils.get_line_item_ds
    orders_ds_fn = utils.get_orders_ds

    # first call one time to cache in case we don't include the IO times
    line_item_ds_fn()
    orders_ds_fn()

    def query() -> pd.DataFrame:
        line_item_ds = line_item_ds_fn()
        orders_ds = orders_ds_fn()

        var1 = date(1993, 7, 1)
        var2 = date(1993, 10, 1)

        orders_filtered = orders_ds[
            (orders_ds["o_orderdate"] >= var1) & (orders_ds["o_orderdate"] < var2)
        ]
        lineitem_filtered = line_item_ds[
            line_item_ds["l_commitdate"] < line_item_ds["l_receiptdate"]
        ]

        jn = lineitem_filtered.merge(
            orders_filtered, left_on="l_orderkey", right_on="o_orderkey"
        )

        jn = jn.drop_duplicates(subset=["o_orderpriority", "l_orderkey"])

        gb = jn.groupby("o_orderpriority", as_index=False)
        agg = gb.agg(order_count=pd.NamedAgg(column="o_orderkey", aggfunc="count"))

        result_df = agg.sort_values(["o_orderpriority"])

        return result_df  # type: ignore[no-any-return]

    utils.run_query(Q_NUM, query)


if __name__ == "__main__":
    q()
