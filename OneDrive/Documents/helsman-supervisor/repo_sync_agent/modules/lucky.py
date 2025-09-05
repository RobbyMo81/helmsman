import random  # Python's random module
from datetime import datetime, timezone
import os
import logging

logger = logging.getLogger(__name__)

# Ensure optional dependencies are handled and names exist for static analysis
SKLEARN_AVAILABLE = False
KMeans = None
np = None
try:
    from sklearn.cluster import KMeans as _KMeans
    import numpy as _np

    KMeans = _KMeans
    np = _np
    SKLEARN_AVAILABLE = True
except Exception:
    # If sklearn is not available, try to keep numpy if possible
    try:
        import numpy as _np

        np = _np
    except Exception:
        np = None


def load_powerball_draws(numbers_file, n_main=5):
    """Load draws from a file. Each line: n_main numbers + 1 powerball, comma or space separated."""
    draws = []
    if not numbers_file or not os.path.isfile(numbers_file):
        return None
    with open(numbers_file, "r") as f:
        for line in f:
            parts = [int(x) for x in line.replace(",", " ").split() if x.isdigit()]
            if len(parts) == n_main + 1:
                draws.append(parts[:n_main])
    return np.array(draws) if np is not None and draws else None


def ml_generate_numbers(n_main=5, n_range=69, pb_range=26, numbers_file=None):
    # Use real draws if file provided, else simulate
    draws = load_powerball_draws(numbers_file, n_main) if numbers_file else None
    if draws is None and SKLEARN_AVAILABLE and np is not None:
        draws = np.random.randint(1, n_range + 1, size=(100, n_main))
    if (
        SKLEARN_AVAILABLE
        and KMeans is not None
        and np is not None
        and draws is not None
    ):
        # Cluster to find 'hot' numbers
        kmeans = KMeans(n_clusters=n_main, n_init=10)
        kmeans.fit(draws)
        centers = kmeans.cluster_centers_.astype(int).flatten()
        main_numbers = sorted(set(int(x) for x in centers))[:n_main]
        powerball = int(np.random.randint(1, pb_range + 1))
        ticket = main_numbers + [powerball]
        # Ensure all numbers are Python int
        return [int(x) for x in ticket]
    else:
        # Fallback: random sample using Python's random module
        main_numbers = random.sample(range(1, n_range + 1), n_main)
        powerball = random.randint(1, pb_range)
        return main_numbers + [powerball]


def powerball_easter_egg(numbers_file=None):
    logger.info("Powerball Analyzer Activated (ML mode)")
    ticket = ml_generate_numbers(numbers_file=numbers_file)
    logger.info("Your ML-generated ticket: %s", ticket)
    try:
        with open("powerball_manifest.txt", "w", encoding="utf-8") as f:
            f.write(
                f"Suggested ticket: {ticket} @ {datetime.now(timezone.utc).isoformat()}\n"
            )
            f.write("Fortune: Your repo is clean. Your luck is pending.\n")
        logger.info("Wrote powerball_manifest.txt")
    except Exception:
        logger.exception("Failed to write powerball_manifest.txt")
