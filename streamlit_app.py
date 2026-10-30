import streamlit as st
from pydantic import ValidationError
from chronos_x.models import CrisisInput
from chronos_x.optimizer import decide_crisis

st.set_page_config(page_title="CHRONOS-X", layout="wide")
st.title("CHRONOS-X Incident Command")
st.write("Paste the current crisis input as JSON. The decision below uses only this input.")
default_input = """{
  "scenario_id": "CHRONOS-2035-001",
  "current_time": "08:00:00",
  "catastrophe_deadline_minutes": 90,
  "observations": [
    {"source": "REACTOR_SENSOR_14", "temperature": 91.8,
     "confidence": 0.31, "timestamp": "07:56:20"},
    {"source": "MAINTENANCE_AGENT", "message": "Cooling system operational",
     "confidence": 0.87, "timestamp": "07:58:10"}
  ],
  "available_interventions": [
    "SHUTDOWN_REACTOR", "ISOLATE_NETWORK",
    "ACTIVATE_BACKUP_COOLING", "CONTINUE_MONITORING"
  ]
}"""
raw_input = st.text_area("Crisis input (JSON)", value=default_input, height=320)

if st.button("Assess crisis", type="primary"):
    try:
        crisis = CrisisInput.model_validate_json(raw_input)
        st.json(decide_crisis(crisis))
    except (ValueError, ValidationError) as error:
        st.error(f"Invalid crisis input: {error}")
