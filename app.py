# Import important python libraries
import streamlit as st
import mysql.connector
import pandas as pd
from streamlit_option_menu import option_menu
import plotly.graph_objects as go


# Connect to MySQL database
#db = mysql.connector.connect(host="34.142.157.237",user="wunchana",password="wunchana", database="world_university_rankings_2023")

# Retrieve secrets from Streamlit
db_host = st.secrets['db_host']
db_user = st.secrets['db_user']
db_pass = st.secrets['db_pass']
db_name = st.secrets['db_name']

# Connect to the database
db = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_pass,
    database=db_name
)

# Create a cursor object 
cursor = db.cursor()
cursor.execute("USE world_university_rankings_2023")

# Build a web app using Python with Streamlit
st.title('Top gl\U0001F30Dbal universities 2023')
with st.sidebar:
    choose = option_menu("Main Menu", ["About", 
                                       "Top global universities", 
                                       "The best university in each country",
                                       "Top universities based on QS ranking indicators",
                                       "Radar chart",
                                       "CRUD",
                                       "Contact"],
                             icons=['house', 
                                    'kanban', 
                                    'kanban',
                                    'kanban',
                                    'kanban',
                                    'kanban',
                                    'person lines fill'],
                             
                             menu_icon="app-indicator", default_index=0)
if choose == "About":
    st.subheader("ℹ️ Web Information")
    st.write('\U0001F3DB The QS World University Rankings (QS-WUR) is one of the most important university ranking systems in the world. This web application provides a user-friendly web application database that allows users to interact with the dataset from Kaggle QS-WUR 2023.')
    st.write('\U0001F4BE About Dataset: The QS World University Rankings® 2023, including almost 1,500 institutions from around the world, based on 8 key ranking indicators (ar, er, fsr, cpf, ifr, isr, irn, and ger).')
    st.write('\U0001F4DD Remark: Academic reputation (ar), Employer reputation (er), Faculty/student ratio (fsr), Citations per faculty (cpf), International faculty ratio (ifr), and International student ratio (isr), International research network (irn), Employment outcomes (ger).')

elif choose == "Top global universities":
    st.subheader("\U0001F31F Top Global Universities")
    num = st.selectbox('Select the Number of Top Universities', [10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    # Query to SELECT the top global universities based on QS ranking
    query_top = f"SELECT university.institution, university.rank, university_location.location FROM university JOIN university_location ON university.location_code = university_location.location_code ORDER BY rank ASC LIMIT {num}"
    cursor.execute(query_top)
    top_universities = cursor.fetchall()
    df = pd.DataFrame(top_universities, columns=['Institution', 'QS-Ranking', 'Country'])
    result_container = st.empty()
    result_container.dataframe(df)

elif choose == "The best university in each country":
    st.subheader("\U0001F31F The Best University in Each Country")
    query_best_university = "SELECT university_location.location, university.institution, university.rank FROM university JOIN university_location ON university.location_code = university_location.location_code WHERE university.rank = (SELECT MIN(rank) FROM university u WHERE u.location_code = university.location_code) ORDER BY university_location.location"
    cursor.execute(query_best_university)
    best_universities = cursor.fetchall()
    df = pd.DataFrame(best_universities, columns=['Country', 'Best University', 'QS-Ranking'])
    countries = sorted(df['Country'].unique())     # Option to select country
    selected_country = st.selectbox('Select a Country', countries)
    filtered_df = df[df['Country'] == selected_country]
    result_container = st.empty()
    result_container.dataframe(filtered_df)
    
elif choose == "Top universities based on QS ranking indicators":
    st.subheader("\U0001F31F Top \U0001F51F Universities Based on QS Ranking Indicators")
    st.write('\U0001F4DD Remark: Academic reputation (ar), Employer reputation (er), Faculty/student ratio (fsr), Citations per faculty (cpf), International faculty ratio (ifr), and International student ratio (isr), International research network (irn), Employment outcomes (ger).')
    ranking_indicators = {'AR score': 'ar_score', 'ER score': 'er_score', 'FSR score': 'fsr_score', 'CPF score': 'cpf_score', 'IFR score': 'ifr_score', 'ISR score': 'isr_score', 'IRN score': 'irn_score', 'GER score': 'ger_score'}
    selected_indicator = st.selectbox('Select a QS Ranking Indicator', list(ranking_indicators.keys()))
    # Query to SELECT the top universities based on the selected QS ranking indicator
    query_top = f"SELECT university.institution, university.rank, ranking.{ranking_indicators[selected_indicator]} FROM university JOIN ranking ON university.rank = ranking.rank ORDER BY ranking.{ranking_indicators[selected_indicator]} DESC LIMIT 10"
    cursor.execute(query_top)
    top_universities = cursor.fetchall()
    df = pd.DataFrame(top_universities, columns=['Institution', 'QS-Ranking', selected_indicator])
    result_container = st.empty()
    result_container.dataframe(df)

# Create a Plot Radar chart of 'institution' using QS ranking indicators
elif choose == "Radar chart":
    st.subheader("\U0001F4C8 Radar chart")
    query_universities = "SELECT institution FROM university ORDER BY rank ASC"
    cursor.execute(query_universities)
    universities = [result[0] for result in cursor.fetchall()]
    selected_university = st.selectbox('Select a University', universities)
    query_radar_chart = f"""SELECT university.institution, ranking.ar_score,ranking.er_score, ranking.fsr_score, ranking.cpf_score, ranking.ifr_score, ranking.isr_score, ranking.irn_score, ranking.ger_score
                        FROM ranking
                        JOIN university ON ranking.rank = university.rank
                        WHERE university.institution = '{selected_university}'"""
    cursor.execute(query_radar_chart)
    radar_chart = cursor.fetchall()
    df = pd.DataFrame(radar_chart, columns=['institution', 'ar_score', 'er_score', 'fsr_score', 'cpf_score', 'ifr_score', 'isr_score', 'irn_score', 'ger_score'])
    fig = go.Figure() 
    fig.add_trace(go.Scatterpolar(r=[df['ar_score'][0], df['er_score'][0], df['fsr_score'][0], df['cpf_score'][0], df['ifr_score'][0], df['isr_score'][0], df['irn_score'][0], df['ger_score'][0]],
                              theta=['AR score', 'ER score', 'FSR score', 'CPF score', 'IFR score', 'ISR score', 'IRN score', 'GER score', 'ER score'],
                              fill='toself'))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        title={'text': f'{selected_university} QS Ranking Scores',
           'x': 0.5,
           'y': 0.90,
           'xanchor': 'center',
           'yanchor': 'top'})
    st.plotly_chart(fig)

# Create CRUD (Create, Read, Update and Delete) operations
elif choose == "CRUD":
    st.subheader('📈 QS Ranking 2023')
    # Join the ranking and university tables and select relevant fields
    query = """SELECT university.institution, university.rank, ranking.ar_score, ranking.er_score, ranking.fsr_score, ranking.cpf_score, ranking.ifr_score, ranking.isr_score, ranking.irn_score, ranking.ger_score
            FROM ranking JOIN university ON ranking.rank=university.rank"""
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=['Institution', 'QS-Ranking', 'AR Score', 'ER Score', 'FSR Score', 'CPF Score', 'IFR Score', 'ISR Score', 'IRN Score', 'GER Score'])

    max_rank = df['QS-Ranking'].max()
    
    result_container = st.empty()
    result_container.dataframe(df)
    
    st.subheader('🔧 Create, Read, Update and Delete ⚙️')
    menu = ["Create", "Update", "Delete"]
    choice = st.selectbox("Select CRUD operations", menu)
    
    # Create operation
    if choice == "Create":
        st.subheader("Create Record")
    # Show a form for the user to enter the data for a new record
        new_institution = st.text_input("Enter Institution")
        cursor.execute("SELECT MAX(rank) FROM ranking")
        max_rank = cursor.fetchone()[0] + 1
        new_rank = st.number_input("Enter QS-Ranking", min_value=1, max_value=max_rank)
        new_ar_score = st.number_input("Enter AR Score", min_value=0.0)
        new_er_score = st.number_input("Enter ER Score", min_value=0.0)
        new_fsr_score = st.number_input("Enter FSR Score", min_value=0.0)
        new_cpf_score = st.number_input("Enter CPF Score", min_value=0.0)
        new_ifr_score = st.number_input("Enter IFR Score", min_value=0.0)
        new_isr_score = st.number_input("Enter ISR Score", min_value=0.0)
        new_irn_score = st.number_input("Enter IRN Score", min_value=0.0)
        new_ger_score = st.number_input("Enter GER Score", min_value=0.0)
    # Set all rank values to the new_rank
        new_ar_rank = new_rank
        new_er_rank = new_rank
        new_fsr_rank = new_rank
        new_cpf_rank = new_rank
        new_ifr_rank = new_rank
        new_isr_rank = new_rank
        new_irn_rank = new_rank
        new_ger_rank = new_rank
    # The "Save" button for inserting the new record into the database
        if st.button("Save"):
            query = "INSERT INTO ranking (rank, ar_score, ar_rank, er_score, er_rank, fsr_score, fsr_rank, cpf_score, cpf_rank, ifr_score, ifr_rank, isr_score, isr_rank, irn_score, irn_rank, ger_score, ger_rank) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (new_rank, new_ar_score, new_ar_rank, new_er_score, new_er_rank, new_fsr_score, new_fsr_rank, new_cpf_score, new_cpf_rank, new_ifr_score, new_ifr_rank, new_isr_score, new_isr_rank, new_irn_score, new_irn_rank, new_ger_score, new_ger_rank))
            query = "INSERT INTO university (rank, institution, location_code) VALUES (%s, %s, 'RO')"
            cursor.execute(query, (new_rank, new_institution))
            cnx.commit()
            st.success("Record created successfully!")
            
    # Update operation
    elif choice == "Update":
        st.subheader("Update Record")
        universities = sorted(df['Institution'].unique())
        selected_university = st.selectbox("Select a University to Update", universities)
        # Show the current values for the selected university in table form
        current_values = df.loc[df['Institution'] == selected_university].iloc[0]
        st.table(current_values.to_frame().T.reset_index(drop=True))
        # Show a form for the user to enter the new values for the selected university
        new_institution = st.text_input("Enter Institution", value=current_values['Institution'])
        new_rank = st.number_input("Enter QS-Ranking", min_value=1, max_value=max_rank, value=current_values['QS-Ranking'])
        new_ar_score = st.number_input("Enter AR Score", min_value=0.0, value=current_values['AR Score'])
        new_er_score = st.number_input("Enter ER Score", min_value=0.0, value=current_values['ER Score'])
        new_fsr_score = st.number_input("Enter FSR Score", min_value=0.0, value=current_values['FSR Score'])
        new_cpf_score = st.number_input("Enter CPF Score", min_value=0.0, value=current_values['CPF Score'])
        new_ifr_score = st.number_input("Enter IFR Score", min_value=0.0, value=current_values['IFR Score'])
        new_isr_score = st.number_input("Enter ISR Score", min_value=0.0, value=current_values['ISR Score'])
        new_irn_score = st.number_input("Enter IRN Score", min_value=0.0, value=current_values['IRN Score'])
        new_ger_score = st.number_input("Enter GER Score", min_value=0.0, value=current_values['GER Score'])
        # Set all rank values to the new_rank
        new_ar_rank = new_rank
        new_er_rank = new_rank
        new_fsr_rank = new_rank
        new_cpf_rank = new_rank
        new_ifr_rank = new_rank
        new_isr_rank = new_rank
        new_irn_rank = new_rank
        new_ger_rank = new_rank
        # Create a button to update the record
        if st.button("Update Record"):
        # Update the ranking table
            cursor.execute("""
                UPDATE ranking SET ar_score=%s, ar_rank=%s, er_score=%s, 
                er_rank=%s, fsr_score=%s, fsr_rank=%s, 
                cpf_score=%s, cpf_rank=%s, ifr_score=%s, 
                ifr_rank=%s, isr_score=%s, isr_rank=%s, 
                irn_score=%s, irn_rank=%s, ger_score=%s, 
                ger_rank=%s WHERE rank=%s""",
                (new_ar_score, new_ar_rank, new_er_score, 
                new_er_rank, new_fsr_score, new_fsr_rank, 
                new_cpf_score, new_cpf_rank, new_ifr_score, 
                new_ifr_rank, new_isr_score, new_isr_rank, 
                new_irn_score, new_irn_rank, new_ger_score, 
                new_ger_rank, str(current_values['QS-Ranking'])))
            # Update the university table
            cursor.execute("""UPDATE university SET institution=%s WHERE rank=%s""", (new_institution, str(current_values['QS-Ranking'])))
            cnx.commit()
            st.success(f"All record(s) in institution name {selected_university} have been updated")
              
    # Delete operation
    elif choice == "Delete":
        st.subheader("Delete Record")
        # Show a form for the user to enter the name of the institution to delete
        delete_institution = st.text_input("Enter the Institution name to delete")
        if st.button("Delete"):
        # Check if the institution exists in the database
            query = "SELECT rank FROM university WHERE institution = %s"
            cursor.execute(query, (delete_institution,))
            result = cursor.fetchone()
            if not result:
                st.warning(f"Do not found the institution name '{delete_institution}'")
            else:
                # Delete the record(s) from the database
                delete_rank = result[0]
                query = "DELETE FROM ranking WHERE rank = %s"
                cursor.execute(query, (delete_rank,))
                query = "DELETE FROM university WHERE rank = %s"
                cursor.execute(query, (delete_rank,))
                cnx.commit()
                st.success(f"All record(s) in institution name '{delete_institution}' have been deleted")

elif choose == "Contact":
    st.subheader("📬 Contact Information")
    st.write('\U0001F3A8 Author: Wunchana Seubwai')
    st.write('\U0001F4E7 Email: wseubwai@iu.edu')
    st.write('📅 Updated: 20-04-2023')

