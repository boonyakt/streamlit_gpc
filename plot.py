import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

def showdata():
    """
    Function to create and display an enhanced GPC plot with MWD and/or SCB data
    from selected files in st.session_state["GPC"] with improved UI and full-screen plot,
    including export functionality.
    """
    # Add custom CSS for better UI styling with smaller font and narrower sidebar
    st.markdown("""
        <style>
        /* Narrower sidebar */
        .sidebar .sidebar-content {
            width: 200px !important;
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        /* Smaller font for Checkbox labels */
        .stCheckbox > label {
            font-size: 12px;
            color: #333;
            padding: 4px 0;
        }
        /* Smaller font for Subheaders */
        .stSubheader {
            color: #2c3e50;
            font-weight: bold;
            font-size: 14px;
        }
        /* Ensure main content uses full width */
        .main .block-container {
            padding-left: 220px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Check if GPC data exists in session state
    if "GPC" not in st.session_state:
        st.error("No GPC data found in session state!")
        return

    # Get available file keys
    available_files = list(st.session_state["GPC"].keys())
    if not available_files:
        st.warning("No files found in GPC data!")
        return

    # Function to get Sample name from Dataset 1
    def get_sample_name(file_key):
        request_info = st.session_state["GPC"][file_key]["Dataset 1: Request Information"]
        for item in request_info:
            if isinstance(item, dict) and item.get("parameter") == "Sample name:":
                return item.get("data", file_key)
        return file_key

    # Title in main area
    st.title("GPC Comparison Dashboard")

    # Create figure at the beginning to make it available for export
    fig, ax1 = plt.subplots(figsize=(18, 10))

    # Sidebar for controls
    with st.sidebar:
        st.subheader("Control Panel")
        st.subheader("Select Samples")
        selected_files = []
        for file_key in available_files:
            sample_name = get_sample_name(file_key)
            if st.checkbox(sample_name, value=(file_key == available_files[0]), key=file_key):
                selected_files.append(file_key)

        st.subheader("Display Options")
        show_mwd = st.checkbox("Show Molecular Weight Distribution (MWD)", value=True)
        show_scb = st.checkbox("Show Short Chain Branching (SCB)", value=True)

        if not selected_files:
            st.warning("Please select at least one sample to plot!")
            return

        if not (show_mwd or show_scb):
            st.warning("Please select at least one dataset (MWD or SCB) to plot!")
            return

        st.subheader("Operational Menu")
        if st.button("Upload Data"):
            st.session_state.page = 'home'
            st.rerun()

        # Button to export current plot as image
        # นำไปไว้ใน Sidebar หลังจากวาดกราฟแล้ว
        export_clicked = st.button("Export curve to image")

    # Clear the figure before plotting new data
    ax1.clear()
    ax2 = ax1.twinx() if show_scb else None

    # Colors สำหรับ datasets
    colors = ['#1f77b4', '#2ca02c', '#9467bd', '#ff7f0e', '#17becf']
    data_plotted = False

    # Plot data จากไฟล์ที่เลือก
    for idx, file_key in enumerate(selected_files):
        if file_key not in st.session_state["GPC"]:
            st.warning(f"File {file_key} not found in GPC data!")
            continue

        gpc_data = st.session_state["GPC"][file_key]
        mwd_data = gpc_data["Dataset 5: MWD"]
        scb_data = gpc_data["Dataset 6: SCB"]
        sample_name = get_sample_name(file_key)
        color = colors[idx % len(colors)]

        # Plot MWD data
        if show_mwd:
            try:
                ax1.plot(mwd_data["LogM (Column Y)"], mwd_data["MMD (Column Z)"], 
                         color=color, 
                         label=f'{sample_name} - MWD',
                         alpha=0.7,
                         linewidth=2)
                data_plotted = True
            except Exception as e:
                st.error(f"Error plotting MWD for {sample_name}: {e}")

        # Plot SCB data
        if show_scb and ax2:
            try:
                ax2.plot(scb_data["LogM (Column AA)"], scb_data["CH3 / 1000 TC (Column AB)"], 
                         color=color, 
                         linestyle='--',
                         label=f'{sample_name} - SCB',
                         alpha=0.7,
                         linewidth=2)
                data_plotted = True
            except Exception as e:
                st.error(f"Error plotting SCB for {sample_name}: {e}")

    if data_plotted:
        ax1.set_xlabel('LogM', fontsize=14)
        if show_mwd:
            ax1.set_ylabel('MMD', color='#1f77b4', fontsize=14)
            ax1.tick_params(axis='y', labelcolor='#1f77b4', labelsize=12)
            ax1.grid(True, linestyle='--', alpha=0.3)

        if show_scb and ax2:
            ax2.set_ylabel('CH3 / 1000 TC', color='#ff7f0e', fontsize=14)
            ax2.tick_params(axis='y', labelcolor='#ff7f0e', labelsize=12)

        plt.title('GPC Comparison Plot', fontsize=18, pad=20)

        # Combine legends
        if show_mwd and show_scb and ax2:
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, 
                       loc='center left', bbox_to_anchor=(1.1, 0.5),
                       fontsize=12, frameon=True, edgecolor='black')
        elif show_mwd:
            ax1.legend(loc='center left', bbox_to_anchor=(1.1, 0.5),
                       fontsize=12, frameon=True, edgecolor='black')
        elif show_scb and ax2:
            ax2.legend(loc='center left', bbox_to_anchor=(1.1, 0.5),
                       fontsize=12, frameon=True, edgecolor='black')
    else:
        ax1.clear()
        if ax2:
            ax2.clear()
        st.warning("No data available to plot. Please check your selections and data.")

    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

    # ถ้าคลิก Export ให้เรียกฟังก์ชันส่งออกภาพโดยแน่ใจว่า canvas ถูกอัพเดท
    if export_clicked:
        export_plot_to_image(fig)

def export_plot_to_image(fig):
    """
    Export the provided matplotlib figure as a PNG image and trigger immediate download.
    """
    # Force re-drawเพื่อให้แน่ใจว่ากราฟทั้งหมดถูกเรนเดอร์แล้ว
    fig.canvas.draw()
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=300, facecolor='white')
    buf.seek(0)
    
    st.download_button(
        label="Download GPC Comparison Plot",
        data=buf,
        file_name="gpc_comparison_plot.png",
        mime="image/png"
    )
    # ไม่ปิด buf ที่นี่ เพราะ st.download_button จะใช้งานข้อมูลจาก buf ได้ทันที

if __name__ == "__main__":
    showdata()
