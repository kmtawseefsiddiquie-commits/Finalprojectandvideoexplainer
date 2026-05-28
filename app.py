from flask import Flask, render_template_string, request

app = Flask(__name__)

# Database of the components which include Names, Prices(AUD) and Power consumed(Watts)
COMPONENTS = {
    "cpu": {
        "Intel Core i5-13400F ($320)": {"name": "Intel Core i5-13400F", "price": 320, "watts": 65, "tier": "mid"},
        "AMD Ryzen 7 7800X3D ($580)": {"name": "AMD Ryzen 7 7800X3D", "price": 580, "watts": 120, "tier": "high"},
        "Intel Core i9-14900K ($850)": {"name": "Intel Core i9-14900K", "price": 850, "watts": 253, "tier": "ultra"}
    },
    "gpu": {
        "NVIDIA RTX 4060 ($450)": {"name": "NVIDIA RTX 4060", "price": 450, "watts": 115, "tier": "mid"},
        "NVIDIA RTX 4070 Super ($950)": {"name": "NVIDIA RTX 4070 Super", "price": 950, "watts": 220, "tier": "high"},
        "NVIDIA RTX 4090 ($2950)": {"name": "NVIDIA RTX 4090", "price": 2950, "watts": 450, "tier": "ultra"}
    },
    "ram": {
        "16GB DDR5 5600MHz ($90)": {"name": "16GB DDR5 5600MHz", "price": 90, "tier": "mid"},
        "32GB DDR5 6000MHz ($180)": {"name": "32GB DDR5 6000MHz", "price": 180, "tier": "high"}
    },
    "psu": {
        "550W Bronze PSU ($80)": {"name": "550W Bronze PSU", "price": 80, "max_watts": 550},
        "750W Gold PSU ($150)": {"name": "750W Gold PSU", "price": 150, "max_watts": 750},
        "1000W Platinum PSU ($320)": {"name": "1000W Platinum PSU", "price": 320, "max_watts": 1000}
    }
}

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PC Builder & Compatibility Evaluator</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
</head>
<body class="bg-light py-5">
    <div class="container" style="max-width: 800px;">
        <h1 class="mb-4 text-center text-primary">Custom PC Builder Matrix</h1>
        
        <div class="card shadow-sm p-4 mb-4">
            <form method="POST">
                <div class="mb-3">
                    <label class="form-label fw-bold">Select Processor (CPU)</label>
                    <select name="cpu" class="form-select">
                        {% for option in components.cpu.keys() %}
                        <option value="{{ option }}" {% if selections.cpu == option %}selected{% endif %}>{{ option }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label fw-bold">Select Graphics Card (GPU)</label>
                    <select name="gpu" class="form-select">
                        {% for option in components.gpu.keys() %}
                        <option value="{{ option }}" {% if selections.gpu == option %}selected{% endif %}>{{ option }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label fw-bold">Select Memory (RAM)</label>
                    <select name="ram" class="form-select">
                        {% for option in components.ram.keys() %}
                        <option value="{{ option }}" {% if selections.ram == option %}selected{% endif %}>{{ option }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="mb-3">
                    <label class="form-label fw-bold">Select Power Supply (PSU)</label>
                    <select name="psu" class="form-select">
                        {% for option in components.psu.keys() %}
                        <option value="{{ option }}" {% if selections.psu == option %}selected{% endif %}>{{ option }}</option>
                        {% endfor %}
                    </select>
                </div>
                <button type="submit" class="btn btn-primary w-100 fw-bold">Evaluate Configuration</button>
            </form>
        </div>

        {% if result %}
        <div class="card shadow-sm p-4 border-{{ result.status_color }}">
            <h3 class="text-{{ result.status_color }}">System Assessment: {{ result.verdict }}</h3>
            <p class="text-muted small">Total System Power Draw: <strong>{{ result.total_watts }}W</strong> required vs <strong>{{ result.max_watts }}W</strong> provided.</p>
            <hr>
            <h5>Build Diagnostics:</h5>
            <ul>
                {% for log in result.logs %}
                <li>{{ log }}</li>
                {% endfor %}
            </ul>
            <hr>
            <h4 class="text-end">Total Price: <span class="text-success">${{ result.total_price }} AUD</span></h4>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    selections = {"cpu": None, "gpu": None, "ram": None, "psu": None}
    result = None

    if request.method == "POST":
        selections["cpu"] = request.form.get("cpu")
        selections["gpu"] = request.form.get("gpu")
        selections["ram"] = request.form.get("ram")
        selections["psu"] = request.form.get("psu")

        # Fetch the component dictionaries
        selected_cpu = COMPONENTS["cpu"][selections["cpu"]]
        selected_gpu = COMPONENTS["gpu"][selections["gpu"]]
        selected_ram = COMPONENTS["ram"][selections["ram"]]
        selected_psu = COMPONENTS["psu"][selections["psu"]]

        # 1. Price calculations
        total_price = selected_cpu["price"] + selected_gpu["price"] + selected_ram["price"] + selected_psu["price"]

        # 2. Power consumed Calculations
        total_watts = selected_cpu["watts"] + selected_gpu["watts"] + 50 # 50W buffer for motherboard/fans
        max_watts = selected_psu["max_watts"]

        logs = []
        is_viable = True

        # Sufficient power supply check
        if total_watts > max_watts:
            logs.append("❌ CRITICAL: Your Power Supply (PSU) wattage is too low! The PC will crash under load.")
            is_viable = False
        elif max_watts - total_watts > 400:
            logs.append("⚠️ WARNING: Your Power Supply is heavily over-provisioned. You paid for extra wattage you don't need.")
        else:
            logs.append("✅ PSU capacity is perfectly matched to component energy loads.")

        # Component compatibility
        tiers = [selected_cpu["tier"], selected_gpu["tier"], selected_ram["tier"]]
        if "ultra" in tiers and "mid" in tiers:
            logs.append("⚠️ PERFORMANCE BOTTLENECK: Mixing entry-level and ultra-tier parts means one component will severely limit the other.")
            status_color = "warning"
            verdict = "Imbalanced Build (Performance Bottleneck Present)"
        elif not is_viable:
            status_color = "danger"
            verdict = "Hazardous / Will Not Boot"
        else:
            status_color = "success"
            verdict = "Excellent & Highly Optimized Balanced Configuration"

        result = {
            "total_price": total_price,
            "total_watts": total_watts,
            "max_watts": max_watts,
            "logs": logs,
            "verdict": verdict,
            "status_color": status_color
        }

    return render_template_string(HTML_TEMPLATE, components=COMPONENTS, selections=selections, result=result)

if __name__ == "__main__":
    # Runs web server locally on port 5000
    app.run(host="0.0.0.0", port=5000)
