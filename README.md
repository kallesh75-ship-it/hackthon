# CHRONOS-X

Synthetic industrial incident reconstruction prototype for Python 3.11.

## Run

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m pip install -e .
.venv\Scripts\pytest -q
.venv\Scripts\uvicorn chronos_x.api:app --reload
.venv\Scripts\streamlit run streamlit_app.py
```

The Streamlit page accepts a crisis JSON object in its input bar. Click
**Assess crisis** to calculate the risk, causes, intervention, counterfactuals,
and safety result from the submitted observations and available interventions.
The example shown in the input bar is a placeholder and is not used unless
submitted.

API endpoints include `POST /events`, `POST /scenarios/{id}/reconstruct`,
`GET /causes`, `POST /simulate`, `POST /decide`, and `GET /audit`.
`/decide` includes the five-agent JSON exchange, while `/audit` includes
spoof/replay/poison metrics and the seeded benchmark summary.

## Benchmark summary

The default seeded simulator creates 50 components and 1,000 events.
Counterfactuals use 120 runs by default and report mean loss, CVaR,
deadline violation rate, and a normal-approximation 95% confidence interval.

## Known limitations

This is a thin prototype: policy constraints and causal discovery are
illustrative, and the current verifier uses a deterministic policy certificate
rather than a full Z3 proof. All telemetry and outcomes are synthetic; it is
not suitable for operational control or safety-critical decisions.
