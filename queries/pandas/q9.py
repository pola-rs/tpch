from __future__ import annotations

import pandas as pd

from queries.pandas import utils

Q_NUM = 9


def q() -> None:
    lineitem_ds_fn = utils.get_line_item_ds
    nation_ds_fn = utils.get_nation_ds
    orders_ds_fn = utils.get_orders_ds
    part_ds_fn = utils.get_part_ds
    part_supp_ds_fn = utils.get_part_supp_ds
    supplier_ds_fn = utils.get_supplier_ds

    # first call one time to cache in case we don't include the IO times
    lineitem_ds_fn()
    nation_ds_fn()
    orders_ds_fn()
    part_ds_fn()
    part_supp_ds_fn()
    supplier_ds_fn()

    def query() -> pd.DataFrame:
        lineitem_ds = lineitem_ds_fn()
        nation_ds = nation_ds_fn()
        orders_ds = orders_ds_fn()
        part_ds = part_ds_fn()
        part_supp_ds = part_supp_ds_fn()
        supplier_ds = supplier_ds_fn()

        part_ds = part_ds[part_ds["p_name"].str.contains("green", regex=False)]

        jn1 = part_ds.merge(part_supp_ds, left_on="p_partkey", right_on="ps_partkey")
        jn2 = jn1.merge(supplier_ds, left_on="ps_suppkey", right_on="s_suppkey")
        jn3 = jn2.merge(
            lineitem_ds,
            left_on=["p_partkey", "ps_suppkey"],
            right_on=["l_partkey", "l_suppkey"],
        )
        jn4 = jn3.merge(orders_ds, left_on="l_orderkey", right_on="o_orderkey")
        jn5 = jn4.merge(nation_ds, left_on="s_nationkey", right_on="n_nationkey")

        jn5["o_year"] = jn5["o_orderdate"].dt.year
        jn5["amount"] = jn5["l_extendedprice"] * (1.0 - jn5["l_discount"]) - (
            jn5["ps_supplycost"] * jn5["l_quantity"]
        )
        jn5 = jn5.rename(columns={"n_name": "nation"})

        gb = jn5.groupby(["nation", "o_year"], as_index=False, sort=False)
        agg = gb.agg(sum_profit=pd.NamedAgg(column="amount", aggfunc="sum"))
        sorted_df = agg.sort_values(by=["nation", "o_year"], ascending=[True, False])
        result_df = sorted_df.reset_index(drop=True)

        return result_df  # type: ignore[no-any-return]

    utils.run_query(Q_NUM, query)


if __name__ == "__main__":
    q()
