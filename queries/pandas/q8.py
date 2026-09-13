from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from queries.pandas import utils

if TYPE_CHECKING:
    import pandas as pd

Q_NUM = 8


def q() -> None:
    customer_ds_fn = utils.get_customer_ds
    line_item_ds_fn = utils.get_line_item_ds
    nation_ds_fn = utils.get_nation_ds
    orders_ds_fn = utils.get_orders_ds
    part_ds_fn = utils.get_part_ds
    region_ds_fn = utils.get_region_ds
    supplier_ds_fn = utils.get_supplier_ds

    # first call one time to cache in case we don't include the IO times
    customer_ds_fn()
    line_item_ds_fn()
    nation_ds_fn()
    orders_ds_fn()
    part_ds_fn()
    region_ds_fn()
    supplier_ds_fn()

    def query() -> pd.DataFrame:
        customer_ds = customer_ds_fn()
        line_item_ds = line_item_ds_fn()
        nation_ds = nation_ds_fn()
        orders_ds = orders_ds_fn()
        part_ds = part_ds_fn()
        region_ds = region_ds_fn()
        supplier_ds = supplier_ds_fn()

        var1 = "BRAZIL"
        var2 = "AMERICA"
        var3 = "ECONOMY ANODIZED STEEL"
        var4 = date(1995, 1, 1)
        var5 = date(1996, 12, 31)

        n2 = nation_ds.loc[:, ["n_nationkey", "n_name"]]

        part_ds = part_ds[part_ds["p_type"] == var3][["p_partkey", "p_type"]]
        orders_ds = orders_ds[
            (orders_ds["o_orderdate"] >= var4) & (orders_ds["o_orderdate"] <= var5)
        ][["o_orderkey", "o_orderdate", "o_custkey"]]
        region_filtered = region_ds[region_ds["r_name"] == var2][["r_regionkey"]]
        america_nations = nation_ds.merge(
            region_filtered, left_on="n_regionkey", right_on="r_regionkey"
        )[["n_nationkey"]]
        america_customers = customer_ds.merge(
            america_nations, left_on="c_nationkey", right_on="n_nationkey"
        )[["c_custkey", "c_nationkey"]]
        orders_america = orders_ds.merge(
            america_customers, left_on="o_custkey", right_on="c_custkey"
        )

        lineitem_parts = part_ds.merge(
            line_item_ds, left_on="p_partkey", right_on="l_partkey"
        )[["l_orderkey", "l_suppkey", "l_extendedprice", "l_discount", "p_type"]]
        jn = lineitem_parts.merge(
            orders_america, left_on="l_orderkey", right_on="o_orderkey"
        )
        jn_sup = jn.merge(
            supplier_ds[["s_suppkey", "s_nationkey"]],
            left_on="l_suppkey",
            right_on="s_suppkey",
        )
        jn7 = jn_sup.merge(n2, left_on="s_nationkey", right_on="n_nationkey")

        jn7["o_year"] = jn7["o_orderdate"].dt.year
        jn7["volume"] = jn7["l_extendedprice"] * (1.0 - jn7["l_discount"])
        jn7 = jn7.rename(columns={"n_name": "nation"})

        def udf(df: pd.DataFrame) -> float:
            demonimator: float = df["volume"].sum()
            df = df[df["nation"] == var1]
            numerator: float = df["volume"].sum()
            return round(numerator / demonimator, 2)

        gb = jn7.groupby("o_year", as_index=False)
        agg = gb.apply(udf, include_groups=False)
        agg.columns = ["o_year", "mkt_share"]
        result_df = agg.sort_values("o_year")

        return result_df  # type: ignore[no-any-return]

    utils.run_query(Q_NUM, query)


if __name__ == "__main__":
    q()
