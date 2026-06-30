"""Streamlit dashboard for the DevOps Monitoring Dashboard."""

import time

import requests
import streamlit as st

API_URL = "http://localhost:8000"
API_KEY = "dev-secret-key"

st.set_page_config(page_title="DevOps Monitor", layout="wide")
st.title("DevOps Monitoring Dashboard")

tab_metrics, tab_servers = st.tabs(["Metrics", "Servers"])

# --- Tab 1: Metrics ---
with tab_metrics:
    st.header("System Metrics")

    @st.cache_data(ttl=2)
    def fetch_metrics() -> dict:
        """Fetch current metrics from the API."""
        response = requests.get(f"{API_URL}/metrics", timeout=5)
        response.raise_for_status()
        return response.json()

    try:
        metrics = fetch_metrics()

        col1, col2, col3 = st.columns(3)
        col1.metric("CPU %", f"{metrics['cpu_percent']:.1f}%")
        col2.metric("Memory %", f"{metrics['memory_percent']:.1f}%")
        col3.metric("Disk %", f"{metrics['disk_percent']:.1f}%")

        # Accumulate history in session state
        if "metrics_history" not in st.session_state:
            st.session_state.metrics_history = []

        st.session_state.metrics_history.append(
            {
                "cpu_percent": metrics["cpu_percent"],
                "memory_percent": metrics["memory_percent"],
            }
        )

        # Keep only last 60 data points
        if len(st.session_state.metrics_history) > 60:
            st.session_state.metrics_history = st.session_state.metrics_history[-60:]

        st.subheader("CPU & Memory Over Time")
        st.line_chart(
            data=st.session_state.metrics_history,
            y=["cpu_percent", "memory_percent"],
        )

        # Auto-refresh
        time.sleep(2)
        st.rerun()

    except requests.RequestException as e:
        st.error(f"Could not connect to API: {e}")

# --- Tab 2: Servers ---
with tab_servers:
    st.header("Monitored Servers")

    @st.cache_data(ttl=5)
    def fetch_servers() -> list:
        """Fetch the list of monitored servers."""
        response = requests.get(f"{API_URL}/servers", timeout=5)
        response.raise_for_status()
        return response.json()

    try:
        servers_list = fetch_servers()

        if servers_list:
            # Color-code status
            for s in servers_list:
                if s["status"] == "UP":
                    s["status"] = "🟢 UP"
                elif s["status"] == "DEGRADED":
                    s["status"] = "🟡 DEGRADED"
                elif s["status"] == "DOWN":
                    s["status"] = "🔴 DOWN"
                else:
                    s["status"] = "⚪ unknown"

            st.dataframe(servers_list, use_container_width=True)
        else:
            st.info("No servers registered yet.")

    except requests.RequestException as e:
        st.error(f"Could not fetch servers: {e}")

    # --- Add Server Form ---
    st.subheader("Register a New Server")
    with st.form("add_server_form"):
        name = st.text_input("Server Name")
        host = st.text_input("Host", value="localhost")
        port = st.number_input("Port", min_value=1, max_value=65535, value=8000)
        submitted = st.form_submit_button("Add Server")

        if submitted and name:
            try:
                resp = requests.post(
                    f"{API_URL}/servers",
                    json={"name": name, "host": host, "port": int(port)},
                    headers={"X-API-Key": API_KEY},
                    timeout=5,
                )
                if resp.status_code == 201:
                    st.success(f"Server '{name}' registered!")
                    st.cache_data.clear()
                else:
                    st.error(f"Error: {resp.status_code} - {resp.text}")
            except requests.RequestException as e:
                st.error(f"Request failed: {e}")

    # --- Trigger Health Check ---
    st.subheader("Trigger Health Check")
    try:
        raw_servers = requests.get(f"{API_URL}/servers", timeout=5).json()
        if raw_servers:
            server_options = {f"{s['name']} ({s['host']}:{s['port']})": s["id"] for s in raw_servers}
            selected = st.selectbox("Select a server", list(server_options.keys()))
            if st.button("Check Now"):
                server_id = server_options[selected]
                resp = requests.post(f"{API_URL}/servers/{server_id}/check", timeout=5)
                if resp.status_code == 200:
                    st.success(resp.json()["message"])
                    time.sleep(1)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"Error: {resp.status_code}")
    except requests.RequestException:
        pass
