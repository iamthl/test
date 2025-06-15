from typing import Dict, Any

MODEL_CONFIG: Dict[str, Dict[str, Any]] = {
    "vnstock": {
        "sequence_length": 60,
        "input_size": 1,
        "hidden_size": 50,
        "num_layers": 3,
        "output_size": 1,
        "dropout": 0.2
    },
    "index": {
        "sequence_length": 60,
        "input_size": 1,
        "hidden_size": 64,
        "num_layers": 3,
        "output_size": 1,
        "dropout": 0.2
    },
    "forex": {
        "sequence_length": 60,
        "input_size": 1,
        "hidden_size": 32,
        "num_layers": 3,
        "output_size": 1,
        "dropout": 0.2
    },
    # Add more instrument types as needed
} 