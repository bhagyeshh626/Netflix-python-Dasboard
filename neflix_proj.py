#!/usr/bin/env python
# coding: utf-8

from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Netflix Insights", page_icon="N", layout="wide")

DATA_FILE = Path(__file__).with_name("netflix.csv")


@st.cache_data
def load_data(file_path):
	data = pd.read_csv(file_path)
	data["Watch_Date"] = pd.to_datetime(data["Watch_Date"], errors="coerce")
	return data.drop_duplicates()


st.title("Netflix Insights")
st.caption("Explore subscriptions, revenue, and viewing activity")

try:
	netflix = load_data(DATA_FILE)
except FileNotFoundError:
	st.error(f"Could not find the data file: {DATA_FILE.name}")
	st.stop()

required_columns = {
	"Customer_ID", "Region", "Subscription_Plan", "Category", "Type",
	"Rating", "Watch_Count", "Watch_Date", "Watch_Time_Minutes",
	"Monthly_Revenue", "Title", "Device",
}
missing_columns = required_columns.difference(netflix.columns)
if missing_columns:
	st.error("The CSV is missing required columns: " + ", ".join(sorted(missing_columns)))
	st.stop()

with st.sidebar:
	st.header("Filters")
	regions = st.multiselect("Region", sorted(netflix["Region"].dropna().unique()))
	plans = st.multiselect(
		"Subscription plan", sorted(netflix["Subscription_Plan"].dropna().unique())
	)
	categories = st.multiselect("Category", sorted(netflix["Category"].dropna().unique()))

	date_values = netflix["Watch_Date"].dropna()
	if not date_values.empty:
		selected_dates = st.date_input(
			"Watch date",
			value=(date_values.min().date(), date_values.max().date()),
			min_value=date_values.min().date(),
			max_value=date_values.max().date(),
		)
	else:
		selected_dates = None

filtered = netflix.copy()
if regions:
	filtered = filtered[filtered["Region"].isin(regions)]
if plans:
	filtered = filtered[filtered["Subscription_Plan"].isin(plans)]
if categories:
	filtered = filtered[filtered["Category"].isin(categories)]
if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
	start_date, end_date = selected_dates
	filtered = filtered[filtered["Watch_Date"].dt.date.between(start_date, end_date)]
elif selected_dates:
	filtered = filtered[filtered["Watch_Date"].dt.date == selected_dates]

if filtered.empty:
	st.info("No records match these filters. Adjust the selections in the sidebar.")
	st.stop()

metric_columns = st.columns(4)
metric_columns[0].metric("Customers", f"{filtered['Customer_ID'].nunique():,}")
metric_columns[1].metric("Monthly revenue", f"${filtered['Monthly_Revenue'].sum():,.0f}")
metric_columns[2].metric("Average rating", f"{filtered['Rating'].mean():.2f} / 5")
metric_columns[3].metric("Watch time", f"{filtered['Watch_Time_Minutes'].sum():,.0f} min")

st.divider()

left, right = st.columns(2)
with left:
	st.subheader("Revenue by region")
	region_revenue = (
		filtered.groupby("Region", as_index=False)["Monthly_Revenue"]
		.sum()
		.sort_values("Monthly_Revenue", ascending=False)
	)
	st.altair_chart(
		alt.Chart(region_revenue)
		.mark_bar(color="#e50914", cornerRadiusEnd=3)
		.encode(
			x=alt.X("Monthly_Revenue:Q", title="Revenue", axis=alt.Axis(format="$,.0f")),
			y=alt.Y("Region:N", sort="-x", title=None),
			tooltip=["Region", alt.Tooltip("Monthly_Revenue:Q", format="$,.2f")],
		),
		width="stretch",
	)

with right:
	st.subheader("Average rating by plan")
	plan_rating = filtered.groupby("Subscription_Plan", as_index=False)["Rating"].mean()
	st.altair_chart(
		alt.Chart(plan_rating)
		.mark_bar(color="#564d4d", cornerRadiusEnd=3)
		.encode(
			x=alt.X("Subscription_Plan:N", title=None, axis=alt.Axis(labelAngle=0)),
			y=alt.Y("Rating:Q", title="Average rating", scale=alt.Scale(domain=[0, 5])),
			tooltip=["Subscription_Plan", alt.Tooltip("Rating:Q", format=".2f")],
		),
		width="stretch",
	)

left, right = st.columns(2)
with left:
	st.subheader("Revenue by category")
	category_revenue = (
		filtered.groupby("Category", as_index=False)["Monthly_Revenue"]
		.sum()
		.sort_values("Monthly_Revenue", ascending=False)
	)
	st.altair_chart(
		alt.Chart(category_revenue)
		.mark_bar(color="#e50914", cornerRadiusEnd=3)
		.encode(
			x=alt.X("Monthly_Revenue:Q", title="Revenue", axis=alt.Axis(format="$,.0f")),
			y=alt.Y("Category:N", sort="-x", title=None),
			tooltip=["Category", alt.Tooltip("Monthly_Revenue:Q", format="$,.2f")],
		),
		width="stretch",
	)

with right:
	st.subheader("Revenue over time")
	monthly_revenue = (
		filtered.dropna(subset=["Watch_Date"])
		.assign(Month=lambda data: data["Watch_Date"].dt.to_period("M").astype(str))
		.groupby("Month", as_index=False)["Monthly_Revenue"]
		.sum()
	)
	st.altair_chart(
		alt.Chart(monthly_revenue)
		.mark_line(color="#e50914", point=True)
		.encode(
			x=alt.X("Month:O", sort=None, title=None),
			y=alt.Y("Monthly_Revenue:Q", title="Revenue", axis=alt.Axis(format="$,.0f")),
			tooltip=["Month", alt.Tooltip("Monthly_Revenue:Q", format="$,.2f")],
		),
		width="stretch",
	)

left, right = st.columns(2)
with left:
	st.subheader("Viewing by content type")
	type_counts = filtered.groupby("Type", as_index=False).size()
	st.altair_chart(
		alt.Chart(type_counts)
		.mark_arc(innerRadius=55)
		.encode(
			theta=alt.Theta("size:Q"),
			color=alt.Color("Type:N", scale=alt.Scale(range=["#e50914", "#564d4d"])),
			tooltip=["Type", "size"],
		),
		width="stretch",
	)

with right:
	st.subheader("Most-watched titles")
	top_titles = (
		filtered.groupby("Title", as_index=False)["Watch_Count"]
		.sum()
		.nlargest(10, "Watch_Count")
	)
	st.altair_chart(
		alt.Chart(top_titles)
		.mark_bar(color="#564d4d", cornerRadiusEnd=3)
		.encode(
			x=alt.X("Watch_Count:Q", title="Total watches"),
			y=alt.Y("Title:N", sort="-x", title=None),
			tooltip=["Title", "Watch_Count"],
		),
		width="stretch",
	)

with st.expander("View filtered data"):
	st.caption(f"{len(filtered):,} records")
	st.dataframe(filtered, width="stretch", hide_index=True)

