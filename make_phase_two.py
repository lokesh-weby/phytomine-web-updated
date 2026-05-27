import re

with open('templates/admins/admins_req.html', 'r', encoding='utf-8') as f:
    req_content = f.read()

# Extract everything from the start to the end of the Navbar
match = re.search(r'(.*?<!-- Navbar End -->\s*)', req_content, re.DOTALL)
if not match:
    print('Could not find navbar end')
    exit(1)
header_nav = match.group(1)

# Modify the active link in the navbar
header_nav = header_nav.replace('class="nav-item nav-link active">PROVISION</a>', 'class="nav-item nav-link">PROVISION</a>')
header_nav = header_nav.replace('class="nav-item nav-link">PHASE TWO</a>', 'class="nav-item nav-link active">PHASE TWO</a>')

# Phase Two Content
phase_two_body = """
    <!-- Tracking Section -->
    <div class="container-fluid py-5" style="background: url('/static/admins/home/img/carousel-1.jpg') no-repeat center center fixed; background-size: cover; min-height: 100vh;">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    
                    <div style="background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); border-radius: 15px; padding: 40px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
                        <h2 class="text-center mb-4" style="color: #064e3b; font-weight: 700;">Phase Two: Post-Harvest Data</h2>
                        
                        {% if messages %}
                            {% for message in messages %}
                                <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                                    {{ message }}
                                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                                </div>
                            {% endfor %}
                        {% endif %}

                        <!-- Project Selection -->
                        <form method="GET" action="/phase_two/" class="mb-5">
                            <div class="input-group">
                                <span class="input-group-text fw-bold" style="background: #10b981; color: white; border: none;">Select Project ID</span>
                                <select name="project_id" class="form-select" onchange="this.form.submit()" required>
                                    <option value="" disabled {% if not data %}selected{% endif %}>-- Choose a Project --</option>
                                    {% for p in projects %}
                                        <option value="{{ p.project_id }}" {% if data and data.project_id == p.project_id %}selected{% endif %}>
                                            Project {{ p.project_id }} - {{ p.location }}
                                        </option>
                                    {% endfor %}
                                </select>
                            </div>
                        </form>

                        {% if data %}
                        <div class="mb-4">
                            <h4 style="color: #15803d; border-bottom: 2px solid #22c55e; padding-bottom: 5px;">Project Details (Phase 1)</h4>
                            <div class="row mt-3">
                                <div class="col-md-6 mb-3"><strong>Project ID:</strong> {{ data.project_id }}</div>
                                <div class="col-md-6 mb-3"><strong>Location:</strong> {{ data.location }}</div>
                                <div class="col-md-6 mb-3"><strong>Soil Type:</strong> {{ data.soil_type }}</div>
                                <div class="col-md-6 mb-3"><strong>Growth Duration:</strong> {{ data.growth_duration }} days</div>
                                <div class="col-md-6 mb-3"><strong>Initial Fern Biomass:</strong> {{ data.initial_fern_biomass }} g</div>
                                <div class="col-md-6 mb-3"><strong>Initial Soil REE:</strong> {{ data.initial_soil_ree }} mg/kg</div>
                            </div>
                        </div>

                        <form method="POST" action="/phase_two/">
                            {% csrf_token %}
                            <!-- Hidden field to keep track of selected project during POST -->
                            <input type="hidden" name="project_id" value="{{ data.project_id }}">

                            <h4 style="color: #15803d; border-bottom: 2px solid #22c55e; padding-bottom: 5px; margin-bottom: 20px;">Submit Lab & Harvest Data</h4>
                            
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-bold">Final Fern Biomass (g)</label>
                                    <input type="number" step="0.01" class="form-control" name="final_fern_biomass" value="{{ data.final_fern_biomass|default_if_none:'' }}">
                                </div>

                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-bold">Harvested Plant Weight (g)</label>
                                    <input type="number" step="0.01" class="form-control" name="harvested_biomass" value="{{ data.harvested_biomass|default_if_none:'' }}">
                                </div>

                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-bold">Final Soil REE (mg/kg)</label>
                                    <input type="number" step="0.01" class="form-control" name="final_soil_ree" value="{{ data.final_soil_ree|default_if_none:'' }}">
                                </div>
                                
                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-bold">Plant REE Concentration (mg/kg)</label>
                                    <input type="number" step="0.01" class="form-control" name="plant_ree_conc" value="{{ data.plant_ree_conc|default_if_none:'' }}">
                                </div>
                                
                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-bold">Extraction Efficiency (%)</label>
                                    <input type="number" step="0.01" class="form-control" name="extraction_eff" value="{{ data.extraction_eff|default_if_none:'' }}">
                                </div>

                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-bold">Recovery (%)</label>
                                    <input type="number" step="0.01" class="form-control" name="recovery" value="{{ data.recovery|default_if_none:'' }}">
                                </div>

                                <div class="col-md-6 mb-3">
                                    <label class="form-label fw-bold">Safety Index</label>
                                    <input type="number" step="0.01" class="form-control" name="safety_index" value="{{ data.safety_index|default_if_none:'' }}">
                                </div>
                            </div>

                            <div class="text-center mt-4">
                                <button type="submit" class="btn btn-success px-5 py-2 fw-bold" style="background: linear-gradient(to right, #059669, #10b981); border: none; border-radius: 10px;">Submit Phase 2 Data</button>
                            </div>
                        </form>
                        {% else %}
                            <div class="text-center mt-5 text-muted">
                                <i class="fas fa-search fa-4x mb-3"></i>
                                <h4>Select a project above to enter Phase 2 data</h4>
                            </div>
                        {% endif %}

                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

with open('templates/admins/phase_two.html', 'w', encoding='utf-8') as f:
    f.write(header_nav + phase_two_body)
