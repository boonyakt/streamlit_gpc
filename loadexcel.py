import streamlit as st
import pandas as pd
import os



def browseexcel():
    # Title of the Streamlit app
    st.title("Excel Data Extractor - Multiple Files")

    # Initialize session state for GPC if not already present
    if "GPC" not in st.session_state:
        st.session_state["GPC"] = {}

    # File uploader widget to browse and upload multiple Excel files
    uploaded_files = st.file_uploader("Choose Excel files", type=["xls", "xlsx"], accept_multiple_files=True)

    # Process the files if uploaded
    if uploaded_files:
        for uploaded_file in uploaded_files:
            # Determine the file extension
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()

            # Read the Excel file based on its extension
            if file_extension == ".xls":
                df = pd.read_excel(uploaded_file, engine="xlrd", header=None)
            elif file_extension == ".xlsx":
                df = pd.read_excel(uploaded_file, engine="openpyxl", header=None)
            else:
                st.error(f"Unsupported file format for {uploaded_file.name}. Please upload a .xls or .xlsx file.")
                continue

            # Dictionary to store datasets for this file
            file_data = {}

            # **Dataset 1: Request Information**
            dataset1 = []
            for i in range(4, 8):
                param1 = df.iloc[i, 0]  # Column A
                data1 = df.iloc[i, 1]   # Column B
                dataset1.append({'parameter': param1, 'data': data1})
                param2 = df.iloc[i, 7]  # Column H
                data2 = df.iloc[i, 8]   # Column I
                dataset1.append({'parameter': param2, 'data': data2})
            file_data["Dataset 1: Request Information"] = dataset1

            # **Dataset 2: Results**
            dataset2 = []
            for i in range(28, 36):
                param = df.iloc[i, 0]  # Column A
                data = df.iloc[i, 1]   # Column B
                unit = df.iloc[i, 2] if pd.notna(df.iloc[i, 2]) else ''  # Column C
                dataset2.append({'parameter': param, 'data': data, 'unit': unit})
            file_data["Dataset 2: Results"] = dataset2

            # **Dataset 3: Performance**
            dataset3 = []
            for i in range(28, 31):  # E29:E31
                param = df.iloc[i, 4]  # Column E
                data = df.iloc[i, 5]   # Column F
                unit = df.iloc[i, 6] if pd.notna(df.iloc[i, 6]) else ''  # Column G
                dataset3.append({'parameter': param, 'data': data, 'unit': unit})
            for i in range(37, 42):  # E38:E42
                param = df.iloc[i, 4]
                data = df.iloc[i, 5]
                unit = df.iloc[i, 6] if pd.notna(df.iloc[i, 6]) else ''
                dataset3.append({'parameter': param, 'data': data, 'unit': unit})
            file_data["Dataset 3: Performance"] = dataset3

            # **Dataset 4: Calibration**
            dataset4 = []
            for i in range(28, 36):
                param = df.iloc[i, 7]  # Column H
                data = df.iloc[i, 8]   # Column I
                unit = df.iloc[i, 9] if pd.notna(df.iloc[i, 9]) else ''   # Column J
                dataset4.append({'parameter': param, 'data': data, 'unit': unit})
            file_data["Dataset 4: Calibration"] = dataset4

            # **Dataset 5: MWD**
            dataset5 = {}
            try:
                logm_row = df[df.iloc[:, 24] == "LogM"].index[0]
                logm_data = df.iloc[logm_row + 1:, 24].dropna().tolist()
                dataset5["LogM (Column Y)"] = logm_data
            except IndexError:
                dataset5["LogM (Column Y)"] = "Not found"
            try:
                mmd_row = df[df.iloc[:, 25] == "MMD"].index[0]
                mmd_raw_data = df.iloc[mmd_row + 1:, 25].dropna().tolist()
                mmd_data = [x for x in mmd_raw_data if isinstance(x, (int, float)) and pd.notna(x)]
                dataset5["MMD (Column Z)"] = mmd_data if mmd_data else "No numeric values found"
            except IndexError:
                dataset5["MMD (Column Z)"] = "Not found"
            file_data["Dataset 5: MWD"] = dataset5

            # **Dataset 6: SCB**
            dataset6 = {}
            try:
                logm_scb_row = df[df.iloc[:, 26] == "LogM"].index[0]
                logm_scb_data = df.iloc[logm_scb_row + 1:, 26].dropna().tolist()
                dataset6["LogM (Column AA)"] = logm_scb_data
            except IndexError:
                dataset6["LogM (Column AA)"] = "Not found"
            try:
                ch3_row = df[df.iloc[:, 27] == "CH3 / 1000 TC"].index[0]
                ch3_data = df.iloc[ch3_row + 1:, 27].dropna().tolist()
                dataset6["CH3 / 1000 TC (Column AB)"] = ch3_data
            except IndexError:
                dataset6["CH3 / 1000 TC (Column AB)"] = "Not found"
            file_data["Dataset 6: SCB"] = dataset6

            # Store the file data in session_state using the file name as the key
            st.session_state["GPC"][uploaded_file.name] = file_data

        # Display all data from session_state["GPC"]
        st.write("### All Extracted Data from Session State")
        for file_name, file_data in st.session_state["GPC"].items():
            st.write(f"#### File: {file_name}")
            
            # Display Dataset 1
            st.subheader("Dataset 1: Request Information")
            st.table(file_data["Dataset 1: Request Information"])

            # Display Dataset 2
            st.subheader("Dataset 2: Results")
            st.table(file_data["Dataset 2: Results"])

            # Display Dataset 3
            st.subheader("Dataset 3: Performance")
            st.table(file_data["Dataset 3: Performance"])

            # Display Dataset 4
            st.subheader("Dataset 4: Calibration")
            st.table(file_data["Dataset 4: Calibration"])

            # Display Dataset 5
            st.subheader("Dataset 5: MWD")
            st.write("LogM (Column Y):", file_data["Dataset 5: MWD"]["LogM (Column Y)"])
            st.write("MMD (Column Z):", file_data["Dataset 5: MWD"]["MMD (Column Z)"])

            # Display Dataset 6
            st.subheader("Dataset 6: SCB")
            st.write("LogM (Column AA):", file_data["Dataset 6: SCB"]["LogM (Column AA)"])
            st.write("CH3 / 1000 TC (Column AB):", file_data["Dataset 6: SCB"]["CH3 / 1000 TC (Column AB)"])

            st.write("---")  # Separator between files

            st.session_state.page = 'Plot'
            st.rerun()

    else:
        st.write("No files uploaded yet.")



   