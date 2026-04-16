import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils.api_client import SafeSphereAPI

# Page config
st.set_page_config(
    page_title="SafeSphere - Women Safety System",
    page_icon="🛡️",
    layout="wide"
)

# Initialize API client
if 'api_client' not in st.session_state:
    st.session_state.api_client = SafeSphereAPI()

api = st.session_state.api_client

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'role' not in st.session_state:
    st.session_state.role = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Sidebar navigation
st.sidebar.title("🛡️ SafeSphere")

if not st.session_state.logged_in:
    # Login/Register tabs
    tab1, tab2 = st.sidebar.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True):
            result = api.login(email, password)
            if result:
                st.session_state.logged_in = True
                st.session_state.role = result['role']
                st.session_state.user_id = result['user_id']
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")
    
    with tab2:
        st.subheader("Register")
        reg_name = st.text_input("Name", key="reg_name")
        reg_email = st.text_input("Email", key="reg_email")
        reg_phone = st.text_input("Phone", key="reg_phone")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_role = st.selectbox("Role", ["user", "contact", "admin"], key="reg_role")
        
        if st.button("Register", use_container_width=True):
            result = api.register(reg_email, reg_name, reg_phone, reg_password, reg_role)
            if 'id' in result:
                st.success("Registration successful! Please login.")
            else:
                st.error("Registration failed")

else:
    # Logged in user menu
    st.sidebar.write(f"👤 **{api.role.upper()}**")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        api.clear_token()
        st.session_state.logged_in = False
        st.session_state.role = None
        st.session_state.user_id = None
        st.rerun()
    
    # Navigation based on role
    if api.role == "admin":
        page = st.sidebar.radio(
            "Navigation",
            ["Dashboard", "Active Alerts", "Incidents", "Heatmap", "User Management"]
        )
    else:
        page = st.sidebar.radio(
            "Navigation",
            ["Dashboard", "Emergency Alert", "Location Tracking", "My Contacts", "Alert History"]
        )
    
    # Main content
    st.title(f"🛡️ SafeSphere - {api.role.title()} Dashboard")
    
    if api.role == "admin":
        # Admin Dashboard
        if page == "Dashboard":
            st.header("📊 Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            
            stats = api.get_dashboard_stats()
            
            with col1:
                st.metric("Active Alerts", stats.get('active_alerts', 0))
            with col2:
                st.metric("Today's Alerts", stats.get('today_alerts', 0))
            with col3:
                avg_time = stats.get('avg_response_time_seconds', 0)
                st.metric("Avg Response Time", f"{avg_time:.1f}s")
            with col4:
                st.metric("Total Users", stats.get('total_users', 0))
            
            # Severity distribution
            st.subheader("Alert Severity Distribution")
            severity_data = stats.get('severity_distribution', {})
            if severity_data:
                df = pd.DataFrame(list(severity_data.items()), columns=['Severity', 'Count'])
                fig = px.bar(df, x='Severity', y='Count', title='Alerts by Severity')
                st.plotly_chart(fig, use_container_width=True)
        
        elif page == "Active Alerts":
            st.header("🚨 Active Alerts")
            alerts = api.get_active_alerts()
            
            if alerts:
                for alert in alerts:
                    with st.expander(f"Alert #{alert['id'][:8]} - {alert['status'].upper()}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**User:** {alert.get('user_name', 'Unknown')}")
                            st.write(f"**Phone:** {alert.get('user_phone', 'Unknown')}")
                            st.write(f"**Severity:** {alert['severity']}")
                            st.write(f"**Time:** {alert['triggered_at']}")
                        with col2:
                            st.write(f"**Location:** {alert.get('address', f"Lat: {alert['latitude']}, Lng: {alert['longitude']}")}")
                            if alert['status'] == 'active':
                                if st.button("Acknowledge", key=f"ack_{alert['id']}"):
                                    api.acknowledge_alert(alert['id'])
                                    st.success("Alert acknowledged")
                                    st.rerun()
                            if alert['status'] in ['active', 'acknowledged']:
                                if st.button("Resolve", key=f"res_{alert['id']}"):
                                    api.resolve_alert(alert['id'])
                                    st.success("Alert resolved")
                                    st.rerun()
            else:
                st.info("No active alerts")
        
        elif page == "Incidents":
            st.header("📋 Recent Incidents")
            incidents = api.get_recent_incidents()
            
            if incidents:
                df = pd.DataFrame(incidents)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No incidents reported")
        
        elif page == "Heatmap":
            st.header("🗺️ Incident Heatmap")
            st.info("Heatmap visualization would be displayed here using folium or plotly")
            # In production, you would display an actual map with heatmap layer
            data = api.get_heatmap_data()
            st.write(f"Found {len(data.get('locations', []))} incident locations in the last 30 days")
    
    else:
        # User/Contact Dashboard
        if page == "Dashboard":
            st.header("👋 Welcome to SafeSphere")
            
            col1, col2 = st.columns(2)
            
            with col1:
                user_info = api.get_user_info()
                st.info(f"""
                **Your Details:**
                - Name: {user_info.get('name')}
                - Email: {user_info.get('email')}
                - Phone: {user_info.get('phone')}
                """)
            
            with col2:
                contacts = api.get_contacts()
                st.write(f"**Emergency Contacts:** {len(contacts)}")
                for contact in contacts:
                    st.write(f"📞 {contact['name']} ({contact['relationship']}) - {contact['phone']}")
        
        elif page == "Emergency Alert":
            st.header("🚨 EMERGENCY ALERT")
            st.warning("⚠️ ONLY USE IN REAL EMERGENCIES ⚠️")
            
            col1, col2 = st.columns(2)
            
            with col1:
                latitude = st.number_input("Latitude", value=28.6139, format="%.6f")
                longitude = st.number_input("Longitude", value=77.2090, format="%.6f")
                address = st.text_input("Address", placeholder="Enter address or location description")
                severity = st.selectbox("Severity", ["low", "medium", "high", "critical"])
            
            with col2:
                st.write("### Emergency Button")
                if st.button("🚨 TRIGGER EMERGENCY ALERT 🚨", use_container_width=True, type="primary"):
                    with st.spinner("Triggering alert..."):
                        result = api.trigger_alert(latitude, longitude, address, severity)
                        if 'id' in result:
                            st.success(f"Emergency alert triggered! Alert ID: {result['id'][:8]}")
                            st.balloons()
                        else:
                            st.error("Failed to trigger alert")
        
        elif page == "Location Tracking":
            st.header("📍 Live Location Tracking")
            
            col1, col2 = st.columns(2)
            
            with col1:
                lat = st.number_input("Current Latitude", value=28.6139, format="%.6f")
                lng = st.number_input("Current Longitude", value=77.2090, format="%.6f")
                address = st.text_input("Current Address")
                
                if st.button("Update Location", use_container_width=True):
                    result = api.update_location(lat, lng, address)
                    st.success("Location updated successfully")
            
            with col2:
                st.info("""
                **Location Tracking Active**
                - Updates sent to emergency contacts
                - Real-time monitoring active
                - Location history being recorded
                """)
        
        elif page == "My Contacts":
            st.header("📞 Emergency Contacts")
            
            # Add contact form
            with st.expander("Add New Contact"):
                with st.form("add_contact"):
                    name = st.text_input("Name")
                    phone = st.text_input("Phone Number")
                    email = st.text_input("Email (optional)")
                    relationship = st.text_input("Relationship")
                    is_primary = st.checkbox("Primary Contact")
                    
                    if st.form_submit_button("Add Contact"):
                        result = api.add_contact(name, phone, relationship, email if email else None, is_primary)
                        if 'id' in result:
                            st.success("Contact added successfully")
                            st.rerun()
                        else:
                            st.error("Failed to add contact")
            
            # Display contacts
            contacts = api.get_contacts()
            if contacts:
                for contact in contacts:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(f"**{contact['name']}** ({contact['relationship']})")
                            st.write(f"📞 {contact['phone']}")
                            if contact.get('email'):
                                st.write(f"✉️ {contact['email']}")
                        with col2:
                            if contact.get('is_primary'):
                                st.badge("Primary", color="green")
                        with col3:
                            st.write("")
            else:
                st.info("No emergency contacts added yet")
        
        elif page == "Alert History":
            st.header("📜 Alert History")
            st.info("Alert history would be displayed here")
            # In production, you would fetch and display the user's alert history

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("SafeSphere - Real-time Women Safety System")
