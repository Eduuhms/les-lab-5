"""
Experiment runner: starts the server, collects measurements, saves results to CSV.

Usage:
    python experiment.py
"""

import requests
import time
import csv
import os
import sys
import subprocess
import random

# ── Configuration ─────────────────────────────────────────────────────────────

BASE_URL = "http://127.0.0.1:5000"
N_TRIALS = 30
N_WARMUP = 5
RANDOM_SEED = 42
RESULTS_DIR = "results"
RESULTS_FILE = os.path.join(RESULTS_DIR, "results.csv")

# ── Query Definitions ─────────────────────────────────────────────────────────
# For each scenario, REST returns ALL 20 fields (over-fetching).
# GraphQL returns only the fields required for the use case.

SCENARIOS = {
    "single_book_card": {
        "description": "Single Book — Card View (5 fields needed out of 20)",
        "rest_endpoint": "/api/books/1",
        "graphql_query": """{
  book(id: 1) {
    id
    title
    author_name
    rating
    cover_url
  }
}""",
    },
    "book_list": {
        "description": "Book List — 10 items (4 fields per item needed)",
        "rest_endpoint": "/api/books?limit=10",
        "graphql_query": """{
  books(limit: 10) {
    id
    title
    author_name
    rating
  }
}""",
    },
    "book_full_detail": {
        "description": "Single Book — Detail View (13 fields needed out of 20)",
        "rest_endpoint": "/api/books/1",
        "graphql_query": """{
  book(id: 1) {
    id
    title
    author_name
    author_nationality
    year_published
    genre
    description
    rating
    pages
    publisher
    isbn
    language
    cover_url
  }
}""",
    },
}

# ── Measurement Helpers ───────────────────────────────────────────────────────

SESSION = requests.Session()


def measure_rest(endpoint: str) -> dict:
    url = f"{BASE_URL}{endpoint}"
    t0 = time.perf_counter()
    resp = SESSION.get(url, timeout=10)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    return {
        "response_time_ms": round(elapsed_ms, 4),
        "response_size_bytes": len(resp.content),
        "status_code": resp.status_code,
    }


def measure_graphql(query: str) -> dict:
    url = f"{BASE_URL}/graphql"
    t0 = time.perf_counter()
    resp = SESSION.post(url, json={"query": query}, timeout=10)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    return {
        "response_time_ms": round(elapsed_ms, 4),
        "response_size_bytes": len(resp.content),
        "status_code": resp.status_code,
    }


def wait_for_server(max_retries: int = 40, delay: float = 0.5) -> bool:
    for attempt in range(1, max_retries + 1):
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        print(f"  Aguardando servidor... ({attempt}/{max_retries})", end="\r")
        time.sleep(delay)
    return False


# ── Main ──────────────────────────────────────────────────────────────────────

def run_experiment():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 65)
    print("  GraphQL vs REST — Experimento Controlado")
    print("=" * 65)

    # Start server as subprocess
    print("\n[1/4] Iniciando servidor Flask...")
    server_proc = subprocess.Popen(
        [sys.executable, "server.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        print("[2/4] Aguardando servidor ficar disponível...")
        if not wait_for_server():
            print("\nERRO: Servidor não respondeu. Abortando.")
            server_proc.terminate()
            sys.exit(1)
        print("\n  Servidor disponível em http://localhost:5000")

        rng = random.Random(RANDOM_SEED)
        all_results = []

        print("\n[3/4] Coletando medições...\n")

        for scenario_name, scenario in SCENARIOS.items():
            print(f"  Cenário: {scenario['description']}")

            # Warmup — discard
            for _ in range(N_WARMUP):
                measure_rest(scenario["rest_endpoint"])
                measure_graphql(scenario["graphql_query"])

            # Build randomised trial order to avoid order bias
            trial_list = (
                [("REST", scenario["rest_endpoint"])] * N_TRIALS
                + [("GraphQL", scenario["graphql_query"])] * N_TRIALS
            )
            rng.shuffle(trial_list)

            counts = {"REST": 0, "GraphQL": 0}

            for api_type, query_or_endpoint in trial_list:
                if api_type == "REST":
                    m = measure_rest(query_or_endpoint)
                else:
                    m = measure_graphql(query_or_endpoint)

                counts[api_type] += 1
                all_results.append(
                    {
                        "scenario": scenario_name,
                        "api_type": api_type,
                        "trial": counts[api_type],
                        "response_time_ms": m["response_time_ms"],
                        "response_size_bytes": m["response_size_bytes"],
                        "status_code": m["status_code"],
                    }
                )
                time.sleep(0.02)  # 20 ms between requests

            rest_times = [
                r["response_time_ms"]
                for r in all_results
                if r["scenario"] == scenario_name and r["api_type"] == "REST"
            ]
            gql_times = [
                r["response_time_ms"]
                for r in all_results
                if r["scenario"] == scenario_name and r["api_type"] == "GraphQL"
            ]
            rest_sizes = [
                r["response_size_bytes"]
                for r in all_results
                if r["scenario"] == scenario_name and r["api_type"] == "REST"
            ]
            gql_sizes = [
                r["response_size_bytes"]
                for r in all_results
                if r["scenario"] == scenario_name and r["api_type"] == "GraphQL"
            ]

            print(
                f"    REST   — tempo médio: {sum(rest_times)/len(rest_times):.2f} ms  |  "
                f"tamanho médio: {sum(rest_sizes)/len(rest_sizes):.0f} bytes"
            )
            print(
                f"    GraphQL— tempo médio: {sum(gql_times)/len(gql_times):.2f} ms  |  "
                f"tamanho médio: {sum(gql_sizes)/len(gql_sizes):.0f} bytes"
            )
            print()

        # Save CSV
        fieldnames = [
            "scenario", "api_type", "trial",
            "response_time_ms", "response_size_bytes", "status_code",
        ]
        with open(RESULTS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)

        print(f"[4/4] Resultados salvos em {RESULTS_FILE}")
        print(f"      Total de medições: {len(all_results)}")
        print("\nExperimento concluído com sucesso!\n")

    finally:
        server_proc.terminate()
        server_proc.wait()
        print("Servidor encerrado.")


if __name__ == "__main__":
    run_experiment()
