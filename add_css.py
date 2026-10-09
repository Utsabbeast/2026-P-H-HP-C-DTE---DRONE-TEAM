import sys

css = """
/* ==============================================================================
   LEAFLET CUSTOM CONTROLS ALIGNMENT & THEME
   ============================================================================== */
.leaflet-top.leaflet-left {
    display: flex !important;
    flex-direction: row !important;
    align-items: flex-start !important;
}

/* Give color to zoom controls */
.leaflet-control-zoom a {
    background-color: #002D74 !important;
    color: white !important;
    border-color: #001A4A !important;
}
.leaflet-control-zoom a:hover {
    background-color: #001A4A !important;
    color: white !important;
}

/* Give color and icon to map changing box */
.leaflet-control-layers-toggle {
    background-color: #002D74 !important;
    border-radius: 4px !important;
    background-image: url('data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"%3E%3Cpath d="M12 2L2 7l10 5 10-5-10-5zm0 7.3L4.4 6 12 2.2 19.6 6 12 9.3zM2 12l10 5 10-5-1.5-.7-8.5 4.2-8.5-4.2L2 12zm0 5l10 5 10-5-1.5-.7-8.5 4.2-8.5-4.2L2 17z"/%3E%3C/svg%3E') !important;
    background-size: 20px 20px !important;
    background-position: center !important;
}
.leaflet-control-layers-toggle:hover {
    background-color: #001A4A !important;
}
"""

with open('c:/Users/kakol/OneDrive/Desktop/Coding/Drone/static/css/dashboard.css', 'a', encoding='utf-8') as f:
    f.write(css)
