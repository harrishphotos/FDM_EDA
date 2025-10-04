import os
import json
from urllib.request import Request, urlopen
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from time_analysis import render_time_analysis
from predictions import render_fare_prediction, render_tip_prediction


# Get workspace root dynamically (works both locally and on Streamlit Cloud)
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(WORKSPACE_ROOT, "NYC_YELLOW_TAXI_CLEAN.csv")
PARQUET_PATH = os.path.join(WORKSPACE_ROOT, "NYC_YELLOW_TAXI_CLEAN.parquet")
ZONES_GEOJSON_PATH = os.path.join(WORKSPACE_ROOT, "Docs", "taxi_zones.geojson")


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    if os.path.exists(PARQUET_PATH):
        df = pd.read_parquet(PARQUET_PATH)
    else:
        df = pd.read_csv(
            CSV_PATH,
            parse_dates=["tpep_pickup_datetime", "tpep_dropoff_datetime"],
        )
    # Derived columns
    df["pickup_date"] = df["tpep_pickup_datetime"].dt.date
    df["pickup_month"] = df["tpep_pickup_datetime"].dt.to_period("M").astype(str)
    df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
    df["pickup_dow"] = df["tpep_pickup_datetime"].dt.day_name()
    with np.errstate(divide="ignore", invalid="ignore"):
        df["tip_pct"] = (df["tip_amount"] / df["fare_amount"]).replace([np.inf, -np.inf], np.nan)
    return df


def filter_df(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")
    min_date = df["tpep_pickup_datetime"].min().date()
    max_date = df["tpep_pickup_datetime"].max().date()
    start_date, end_date = st.sidebar.date_input(
        "Pickup date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Filter all views to pickups within this date range",
    )
    mask = (
        (df["tpep_pickup_datetime"].dt.date >= start_date)
        & (df["tpep_pickup_datetime"].dt.date <= end_date)
    )
    return df.loc[mask].copy()


def _read_local_geojson(path: str):
    try:
        with open(path, "rb") as f:
            raw = f.read()
        # Strip BOM and whitespace, detect HTML/404
        text = raw.decode("utf-8-sig", errors="replace").strip()
        if not text or text.startswith("<") or text.startswith("404"):
            return None
        return json.loads(text)
    except Exception:
        return None


def _fetch_geojson(url: str):
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        with urlopen(req, timeout=20) as resp:  # type: ignore
            raw = resp.read()
        text = raw.decode("utf-8-sig", errors="replace").strip()
        if not text or text.startswith("<") or text.startswith("404"):
            return None
        return json.loads(text)
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def load_zones_geojson():
    # Try local file first
    data = _read_local_geojson(ZONES_GEOJSON_PATH)
    if data is not None and isinstance(data, dict) and data.get("features"):
        return data
    # Try remote mirrors and cache locally
    mirrors = [
        "https://raw.githubusercontent.com/toddwschneider/nyc-taxi-data/master/taxi_zones.geojson",
        "https://raw.githubusercontent.com/uber-web/kepler.gl-data/master/nyctrips/data/taxi_zones.geojson",
    ]
    for url in mirrors:
        data = _fetch_geojson(url)
        if data and isinstance(data, dict) and data.get("features"):
            try:
                os.makedirs(os.path.dirname(ZONES_GEOJSON_PATH), exist_ok=True)
                with open(ZONES_GEOJSON_PATH, "w", encoding="utf-8") as f:
                    json.dump(data, f)
            except Exception:
                pass
            return data
    return None


def kpi_cards(df: pd.DataFrame) -> None:
    total_trips = int(len(df))
    total_revenue = float(df["total_amount"].sum(skipna=True))
    avg_fare = float(df["fare_amount"].mean(skipna=True))
    avg_distance = float(df["trip_distance"].mean(skipna=True))
    avg_duration = float(df["trip_duration_min"].mean(skipna=True))
    tip_rate = float(df.loc[df["fare_amount"] > 0, "tip_amount"].sum() / df.loc[df["fare_amount"] > 0, "fare_amount"].sum()) if (df.loc[df["fare_amount"] > 0, "fare_amount"].sum()) else 0.0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Trips", f"{total_trips:,}")
    c2.metric("Revenue", f"${total_revenue:,.0f}")
    c3.metric("Avg Fare", f"${avg_fare:,.2f}")
    c4.metric("Avg Distance", f"{avg_distance:.2f} mi")
    c5.metric("Avg Duration", f"{avg_duration:.1f} min")
    c6.metric("Tip Rate", f"{tip_rate*100:.1f}%")


def tab_overview(df: pd.DataFrame) -> None:
    kpi_cards(df)
    # Human-readable labels for codes
    payment_labels = {1: "Credit card", 2: "Cash", 3: "No charge", 4: "Dispute", 5: "Unknown", 6: "Voided trip"}
    ratecode_labels = {1: "Standard rate", 2: "JFK", 3: "Newark", 4: "Nassau/Westchester", 5: "Negotiated fare", 6: "Group ride"}

    # Payment mix (share of trips by payment type)
    payment_mix = df["payment_type"].dropna().astype(int).map(payment_labels).value_counts(normalize=True).rename_axis("Payment type").reset_index(name="Share of trips")
    fig_mix = px.pie(payment_mix, values="Share of trips", names="Payment type", title="Payment mix by method")
    fig_mix.update_traces(textposition='inside', textinfo='percent+label')

    # Rate code usage
    rc = df["RatecodeID"].dropna().astype(int).map(ratecode_labels).value_counts(normalize=True).rename_axis("Rate code").reset_index(name="Share of trips")
    fig_rc = px.bar(rc, x="Rate code", y="Share of trips", title="Rate code usage")
    fig_rc.update_layout(xaxis_title="Rate code", yaxis_title="Share of trips", yaxis_tickformat=",")

    c1, c2 = st.columns(2)
    c1.plotly_chart(fig_mix, use_container_width=True)
    c2.plotly_chart(fig_rc, use_container_width=True)


def tab_trends(df: pd.DataFrame) -> None:
    st.markdown("""
    The three trend lines below show monthly movement in overall demand, earnings, and pricing proxy.
    Use these to spot seasonality, growth/decline, and potential fare mix shifts.
    """)
    monthly = df.groupby("pickup_month", as_index=False).agg(
        Trips=("VendorID", "count"),
        Revenue=("total_amount", "sum"),
        Avg_Fare=("fare_amount", "mean"),
    )

    fig1 = px.line(monthly, x="pickup_month", y="Trips", markers=True, title="Trips per month", labels={"pickup_month": "Pickup month", "Trips": "Trips"})
    fig1.update_layout(xaxis_title="Pickup month", yaxis_title="Trips")
    st.markdown("**Trips per month**: overall ride volume trend; use this to benchmark demand.")
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.line(monthly, x="pickup_month", y="Revenue", markers=True, title="Revenue per month", labels={"pickup_month": "Pickup month", "Revenue": "Revenue (USD)"})
    fig2.update_layout(xaxis_title="Pickup month", yaxis_title="Revenue (USD)", yaxis_tickprefix="$", yaxis_tickformat=",")
    st.markdown("**Revenue per month**: aggregate earnings (total_amount); track union-level revenue trajectory.")
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.line(monthly, x="pickup_month", y="Avg_Fare", markers=True, title="Average fare per month", labels={"pickup_month": "Pickup month", "Avg_Fare": "Average fare (USD)"})
    fig3.update_layout(xaxis_title="Pickup month", yaxis_title="Average fare (USD)", yaxis_tickprefix="$", yaxis_tickformat=".2f")
    st.markdown("**Average fare per month**: pricing/trip-length proxy; affected by surcharges and route mix.")
    st.plotly_chart(fig3, use_container_width=True)


 


def tab_hotspots(df: pd.DataFrame) -> None:
    st.markdown("""
    Hotspots show where demand concentrates, summarized as a treemap by Borough → Zone.
    Switch between Pickups and Dropoffs. Larger blocks indicate higher volumes.
    """)
    mode = st.radio("Show", ["Pickups", "Dropoffs"], horizontal=True)
    if mode == "Pickups":
        agg = df.groupby(["PU_Borough", "PU_Zone"], as_index=False).agg(Trips=("VendorID", "count"), Revenue=("total_amount", "sum"))
        fig = px.treemap(
            agg,
            path=[px.Constant("NYC"), "PU_Borough", "PU_Zone"],
            values="Trips",
            color="Trips",
            color_continuous_scale="YlOrRd",
            title="Pickup hotspots by borough and zone",
        )
    else:
        agg = df.groupby(["DO_Borough", "DO_Zone"], as_index=False).agg(Trips=("VendorID", "count"), Revenue=("total_amount", "sum"))
        fig = px.treemap(
            agg,
            path=[px.Constant("NYC"), "DO_Borough", "DO_Zone"],
            values="Trips",
            color="Trips",
            color_continuous_scale="YlOrRd",
            title="Dropoff hotspots by borough and zone",
        )
    fig.update_layout(margin=dict(t=50, l=0, r=0, b=0))
    st.plotly_chart(fig, use_container_width=True)


def tab_zones(df: pd.DataFrame) -> None:
    st.markdown("""
    Ranked lists of pickup and dropoff zones by trip count. Use this to identify consistently busy areas for shift planning and resource allocation.
    """)
    top_n = st.slider("Number of zones to display (N)", 5, 30, 15)
    pu = df.groupby("PU_Zone", as_index=False).agg(Trips=("VendorID", "count"), Revenue=("total_amount", "sum"))
    do = df.groupby("DO_Zone", as_index=False).agg(Trips=("VendorID", "count"), Revenue=("total_amount", "sum"))
    pu_top = pu.sort_values("Trips", ascending=False).head(top_n)
    do_top = do.sort_values("Trips", ascending=False).head(top_n)
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.bar(pu_top, x="Trips", y="PU_Zone", orientation="h", title="Top pickup zones", labels={"Trips": "Trips", "PU_Zone": "Pickup zone"}), use_container_width=True)
    c2.plotly_chart(px.bar(do_top, x="Trips", y="DO_Zone", orientation="h", title="Top dropoff zones", labels={"Trips": "Trips", "DO_Zone": "Dropoff zone"}), use_container_width=True)


def tab_flows(df: pd.DataFrame) -> None:
    st.markdown("""
    Origin→destination pairs reveal the most common routes. Use these for targeted driver guidance and matching strategies.
    Below: table of top flows by trips and a Sankey diagram visualizing movement between zones.
    """)
    k = st.slider("Number of flows to show (K)", 5, 50, 20)
    flows = (
        df.groupby(["PU_Zone", "DO_Zone"], as_index=False)
        .agg(Trips=("VendorID", "count"), Revenue=("total_amount", "sum"))
        .sort_values("Trips", ascending=False)
        .head(k)
        .reset_index(drop=True)
    )
    flows.index = flows.index + 1
    st.dataframe(flows.rename(columns={"PU_Zone": "Pickup zone", "DO_Zone": "Dropoff zone"}))

    # Sankey of top flows
    zones = pd.unique(pd.concat([flows["PU_Zone"], flows["DO_Zone"]], ignore_index=True))
    index = {z: i for i, z in enumerate(zones)}
    sources = [index[z] for z in flows["PU_Zone"]]
    targets = [index[z] + len(zones) for z in flows["DO_Zone"]]  # separate target space
    labels = list(zones) + [f"{z}" for z in zones]
    values = flows["Trips"].tolist()
    sankey = go.Figure(
        data=[
            go.Sankey(
                node=dict(label=labels, pad=10, thickness=12),
                link=dict(source=sources, target=targets, value=values),
            )
        ]
    )
    sankey.update_layout(title_text="Top flows by trips")
    st.plotly_chart(sankey, use_container_width=True)


# Removed fares & tips tab per feedback


# Removed congestion tab per feedback


def tab_airports(df: pd.DataFrame) -> None:
    st.markdown("""
    Airport trips are identified by zone names containing "Airport" (JFK, LaGuardia, Newark).
    Below: top 20 airport origin→destination routes.
    """)
    # Heuristic by zone name contains "Airport"
    airport_mask = df["PU_Zone"].str.contains("Airport", case=False, na=False) | df["DO_Zone"].str.contains("Airport", case=False, na=False)
    adf = df.loc[airport_mask]
    st.write(f"**Airport-related trips**: {len(adf):,}")
    flows = (
        adf.groupby(["PU_Zone", "DO_Zone"], as_index=False)
        .agg(Trips=("VendorID", "count"), Revenue=("total_amount", "sum"))
        .sort_values("Trips", ascending=False)
        .head(20)
        .reset_index(drop=True)
    )
    flows.index = flows.index + 1
    st.dataframe(flows.rename(columns={"PU_Zone": "Pickup zone", "DO_Zone": "Dropoff zone"}))


def main() -> None:
    st.set_page_config(page_title="NYC Yellow Taxi – EDA", layout="wide")
    st.title("NYC Yellow Taxi – Exploratory Dashboard")

    df_all = load_data()
    df = filter_df(df_all)

    tabs = st.tabs(["Overview", "Trends", "Time Analysis", "Map", "Hotspots", "Zones", "Flows", "Airports", "Fare Prediction", "Tip Prediction"])
    with tabs[0]:
        tab_overview(df)
    with tabs[1]:
        tab_trends(df)
    with tabs[2]:
        render_time_analysis(df)
    with tabs[3]:
        st.markdown("""
        **Interactive NYC Taxi Zone Heatmap**: Explore pickup and dropoff demand across all 263 official taxi zones.
        Hover over zones to see names, trip counts, and rankings. Use the comparison view to spot imbalances.
        """)
        geojson = load_zones_geojson()
        
        col1, col2 = st.columns([1, 1])
        with col1:
            mode = st.radio("Show", ["Pickups", "Dropoffs", "Side-by-side"], horizontal=True, key="map_mode")
        
        show_top = False
        with col2:
            if mode != "Side-by-side":
                show_top = st.checkbox("Show top 10 zones summary", value=True)
        if geojson is None:
            st.info("Taxi zone shapes unavailable. Upload a taxi_zones.geojson below or we will show a borough-level fallback.")
            uploaded = st.file_uploader("Upload NYC taxi zones GeoJSON", type=["geojson", "json"], accept_multiple_files=False)
            if uploaded is not None:
                try:
                    content = uploaded.read()
                    text = content.decode("utf-8-sig", errors="replace").strip()
                    obj = json.loads(text)
                    if isinstance(obj, dict) and obj.get("features"):
                        os.makedirs(os.path.dirname(ZONES_GEOJSON_PATH), exist_ok=True)
                        with open(ZONES_GEOJSON_PATH, "w", encoding="utf-8") as f:
                            json.dump(obj, f)
                        st.success("GeoJSON uploaded and cached. Please toggle the Show control or reload to render the map.")
                        # Clear cache to reload
                        load_zones_geojson.clear()
                        geojson = obj
                    else:
                        st.error("Uploaded file is not a valid GeoJSON FeatureCollection.")
                except Exception as e:
                    st.error(f"Failed to parse uploaded GeoJSON: {e}")
        if geojson is None:
            st.info("Showing borough-level hotspot map as a fallback.")
            # Fallback: borough-level bubble map using known centroids (approximate)
            borough_coords = {
                "Manhattan": (40.7831, -73.9712),
                "Brooklyn": (40.6782, -73.9442),
                "Queens": (40.7282, -73.7949),
                "Bronx": (40.8448, -73.8648),
                "Staten Island": (40.5795, -74.1502),
                "EWR": (40.6895, -74.1745),  # Newark Airport
            }
            if mode == "Pickups":
                agg = df.groupby("PU_Borough", as_index=False).agg(Trips=("VendorID", "count"))
                agg = agg.rename(columns={"PU_Borough": "Borough"})
                title = "Pickup hotspots by borough"
            else:
                agg = df.groupby("DO_Borough", as_index=False).agg(Trips=("VendorID", "count"))
                agg = agg.rename(columns={"DO_Borough": "Borough"})
                title = "Dropoff hotspots by borough"
            agg["lat"] = agg["Borough"].map(lambda b: borough_coords.get(b, (None, None))[0])
            agg["lon"] = agg["Borough"].map(lambda b: borough_coords.get(b, (None, None))[1])
            agg = agg.dropna(subset=["lat", "lon"])
            fig = px.scatter_mapbox(
                agg,
                lat="lat",
                lon="lon",
                size="Trips",
                color="Trips",
                color_continuous_scale="YlOrRd",
                size_max=60,
                zoom=9,
                hover_name="Borough",
                hover_data={"Trips": True, "lat": False, "lon": False},
                title=title,
                mapbox_style="open-street-map",
            )
            st.plotly_chart(fig, use_container_width=True)
        elif geojson is not None:
            props = geojson.get("features", [{}])[0].get("properties", {})
            # Detect ID field (case-insensitive)
            id_field = None
            zone_field = None
            borough_field = None
            for key in props.keys():
                if key.lower() == 'locationid':
                    id_field = key
                if key.lower() == 'zone':
                    zone_field = key
                if key.lower() == 'borough':
                    borough_field = key
            if id_field is None:
                id_field = 'OBJECTID' if 'OBJECTID' in props else 'objectid'
            feature_key = f"properties.{id_field}"
            
            # Build zone name mapping from GeoJSON
            zone_map = {}
            borough_map = {}
            if zone_field and borough_field:
                for feat in geojson['features']:
                    loc_id = feat['properties'].get(id_field)
                    zone_map[loc_id] = feat['properties'].get(zone_field, 'Unknown')
                    borough_map[loc_id] = feat['properties'].get(borough_field, 'Unknown')
            
            if mode == "Side-by-side":
                # Show both pickups and dropoffs
                pu_agg = df.groupby("PULocationID", as_index=False).agg(Trips=("VendorID", "count"))
                pu_agg = pu_agg.rename(columns={"PULocationID": "LocationID", "Trips": "Pickups"})
                do_agg = df.groupby("DOLocationID", as_index=False).agg(Trips=("VendorID", "count"))
                do_agg = do_agg.rename(columns={"DOLocationID": "LocationID", "Trips": "Dropoffs"})
                agg = pu_agg.merge(do_agg, on="LocationID", how="outer").fillna(0)
                agg["Net_Flow"] = agg["Pickups"] - agg["Dropoffs"]
                
                sample_geojson_id = geojson['features'][0]['properties'].get(id_field)
                if isinstance(sample_geojson_id, str):
                    agg["LocationID"] = agg["LocationID"].astype(str)
                else:
                    agg["LocationID"] = agg["LocationID"].astype(int)
                
                agg["Zone"] = agg["LocationID"].map(zone_map)
                agg["Borough"] = agg["LocationID"].map(borough_map)
                
                c1, c2 = st.columns(2)
                with c1:
                    fig1 = px.choropleth(
                        agg,
                        geojson=geojson,
                        locations="LocationID",
                        featureidkey=feature_key,
                        color="Pickups",
                        color_continuous_scale="YlOrRd",
                        hover_data={"Zone": True, "Borough": True, "Pickups": ":,", "LocationID": False},
                        title="Pickups by zone",
                    )
                    fig1.update_geos(fitbounds="locations", visible=False)
                    fig1.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, coloraxis_colorbar_title_text="Pickups")
                    st.plotly_chart(fig1, use_container_width=True)
                
                with c2:
                    fig2 = px.choropleth(
                        agg,
                        geojson=geojson,
                        locations="LocationID",
                        featureidkey=feature_key,
                        color="Dropoffs",
                        color_continuous_scale="Blues",
                        hover_data={"Zone": True, "Borough": True, "Dropoffs": ":,", "LocationID": False},
                        title="Dropoffs by zone",
                    )
                    fig2.update_geos(fitbounds="locations", visible=False)
                    fig2.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, coloraxis_colorbar_title_text="Dropoffs")
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Net flow viz
                st.markdown("**Net Flow**: Positive = more pickups (origins), Negative = more dropoffs (destinations)")
                fig3 = px.choropleth(
                    agg,
                    geojson=geojson,
                    locations="LocationID",
                    featureidkey=feature_key,
                    color="Net_Flow",
                    color_continuous_scale="RdBu_r",
                    color_continuous_midpoint=0,
                    hover_data={"Zone": True, "Borough": True, "Net_Flow": ":,", "Pickups": ":,", "Dropoffs": ":,", "LocationID": False},
                    title="Net flow (Pickups − Dropoffs)",
                )
                fig3.update_geos(fitbounds="locations", visible=False)
                fig3.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, coloraxis_colorbar_title_text="Net Flow")
                st.plotly_chart(fig3, use_container_width=True)
                
            else:
                if mode == "Pickups":
                    agg = df.groupby("PULocationID", as_index=False).agg(Trips=("VendorID", "count"))
                    agg = agg.rename(columns={"PULocationID": "LocationID"})
                    title = "Pickup demand by taxi zone"
                    color_scale = "YlOrRd"
                else:
                    agg = df.groupby("DOLocationID", as_index=False).agg(Trips=("VendorID", "count"))
                    agg = agg.rename(columns={"DOLocationID": "LocationID"})
                    title = "Dropoff demand by taxi zone"
                    color_scale = "Blues"
                
                # Match ID type from GeoJSON
                sample_geojson_id = geojson['features'][0]['properties'].get(id_field)
                if isinstance(sample_geojson_id, str):
                    agg["LocationID"] = agg["LocationID"].astype(str)
                else:
                    agg["LocationID"] = agg["LocationID"].astype(int)
                
                agg["Zone"] = agg["LocationID"].map(zone_map)
                agg["Borough"] = agg["LocationID"].map(borough_map)
                agg["Rank"] = agg["Trips"].rank(ascending=False, method="min").astype(int)
                
                # Top zones summary
                if show_top:
                    top10 = agg.nlargest(10, "Trips")[["Zone", "Borough", "Trips"]].reset_index(drop=True)
                    top10.index = top10.index + 1
                    st.markdown(f"**Top 10 {mode} zones**")
                    st.dataframe(top10, use_container_width=True, height=280)
                
                fig = px.choropleth(
                    agg,
                    geojson=geojson,
                    locations="LocationID",
                    featureidkey=feature_key,
                    color="Trips",
                    color_continuous_scale=color_scale,
                    hover_data={"Zone": True, "Borough": True, "Trips": ":,", "Rank": True, "LocationID": False},
                    title=title,
                )
                fig.update_geos(fitbounds="locations", visible=False)
                fig.update_layout(
                    margin={"r":0,"t":50,"l":0,"b":0},
                    coloraxis_colorbar_title_text="Trips"
                )
                st.plotly_chart(fig, use_container_width=True)
    with tabs[4]:
        tab_hotspots(df)
    with tabs[5]:
        tab_zones(df)
    with tabs[6]:
        tab_flows(df)
    with tabs[7]:
        tab_airports(df)
    with tabs[8]:
        render_fare_prediction(df)
    with tabs[9]:
        render_tip_prediction(df)


if __name__ == "__main__":
    main()


