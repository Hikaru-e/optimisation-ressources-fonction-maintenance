import streamlit as st
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpStatus, LpBinary
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Introduction
st.title("Optimisation des Ressources de la Fonction Maintenance")
st.markdown("""
Cette application permet d'optimiser l'allocation des tâches de maintenance en fonction des ressources humaines et des outils disponibles. 
Saisissez les tâches, les ressources humaines et les outils pour voir comment optimiser leur utilisation.
""")

# Function to load data from a CSV file
def load_data(file):
    df = pd.read_csv(file)
    return df

# Manual input for tasks, resources, and tools
def manual_input():
    st.header("Saisie des Tâches")
    task_rows = st.number_input("Nombre de Tâches", min_value=1, value=1, step=1, key="num_tasks")
    tasks_input = [st.text_input(f"Tâche {i+1}", key=f"task_input_{i}") for i in range(task_rows)]
    tasks_duration = {task: st.number_input(f"Durée de {task} (heures)", min_value=1, key=f"task_duration_{i}_{task}") for i, task in enumerate(tasks_input)}

    st.header("Saisie des Ressources Humaines")
    resource_rows = st.number_input("Nombre de Ressources Humaines", min_value=1, value=1, step=1, key="num_resources")
    resources_input = [st.text_input(f"Ressource Humaine {i+1}", key=f"resource_input_{i}") for i in range(resource_rows)]
    resources_availability = {res: st.number_input(f"Disponibilité de {res} (heures)", min_value=1, key=f"resource_availability_{i}") for i, res in enumerate(resources_input)}

    st.header("Saisie des Outillages")
    tool_rows = st.number_input("Nombre d'Outillages", min_value=1, value=1, step=1, key="num_tools")
    tools_input = [st.text_input(f"Outillage {i+1}", key=f"tool_input_{i}") for i in range(tool_rows)]
    tools_availability = {tool: st.number_input(f"Disponibilité de {tool} (heures)", min_value=1, key=f"tool_availability_{i}") for i, tool in enumerate(tools_input)}

    st.header("Dépendances des Tâches")
    dependencies = {}
    for i, task in enumerate(tasks_input):
        dependencies[task] = st.multiselect(f"Tâches prérequises pour {task}", tasks_input, key=f"dependencies_{i}_{task}")

    st.header("Priorité des Tâches")
    task_priority = {task: st.slider(f"Priorité de {task}", min_value=1, max_value=10, value=5, key=f"priority_{task}") for i, task in enumerate(tasks_input)}

    return tasks_input, tasks_duration, resources_input, resources_availability, tools_input, tools_availability, dependencies, task_priority

# File uploader for all data
def file_upload_all():
    st.header("Importation des Données")
    all_data_file = st.file_uploader("Importer toutes les données (tâches, ressources et outils)", type=["csv"], key="all_data_upload")

    if all_data_file is not None:
        try:
            all_data_df = load_data(all_data_file)

            if all_data_df.empty or any(col not in all_data_df.columns for col in ['Tâche', 'Durée', 'Ressource Humaine', 'Disponibilité', 'Outillage', 'Disponibilité des outils', 'Dépendances', 'Priorité']):
                st.error("Le fichier importé ne correspond pas au format attendu.")
                return None, None, None, None, None, None, None, None

            tasks_input = all_data_df['Tâche'].tolist()
            tasks_duration = all_data_df.set_index('Tâche')['Durée'].to_dict()
            resources_input = all_data_df['Ressource Humaine'].unique().tolist()
            resources_availability = all_data_df.groupby('Ressource Humaine')['Disponibilité'].sum().to_dict()
            tools_input = all_data_df['Outillage'].unique().tolist()
            tools_availability = all_data_df.groupby('Outillage')['Disponibilité des outils'].sum().to_dict()

            dependencies = all_data_df.groupby('Tâche')['Dépendances'].apply(lambda x: [item for sublist in x.dropna().str.split(',').tolist() for item in sublist]).to_dict()
            task_priority = all_data_df.set_index('Tâche')['Priorité'].to_dict()

            st.write("Données importées:")
            st.write(all_data_df)

            return tasks_input, tasks_duration, resources_input, resources_availability, tools_input, tools_availability, dependencies, task_priority

        except Exception as e:
            st.error(f"Une erreur s'est produite lors du traitement du fichier : {str(e)}")
            return None, None, None, None, None, None, None, None
    else:
        st.warning("Veuillez importer un fichier au format CSV.")
        return None, None, None, None, None, None, None, None

# File uploader for resources data
def file_upload_resources():
    st.header("Importation des Ressources Humaines")
    resources_file = st.file_uploader("Importer les données des Ressources Humaines", type=["csv"], key="resources_upload")

    if resources_file is not None:
        try:
            resources_df = load_data(resources_file)

            if resources_df.empty or any(col not in resources_df.columns for col in ['Ressource Humaine', 'Disponibilité']):
                st.error("Le fichier importé ne correspond pas au format attendu.")
                return None, None

            resources_input = resources_df['Ressource Humaine'].unique().tolist()
            resources_availability = resources_df.set_index('Ressource Humaine')['Disponibilité'].to_dict()

            st.write("Données importées:")
            st.write(resources_df)

            return resources_input, resources_availability

        except Exception as e:
            st.error(f"Une erreur s'est produite lors du traitement du fichier : {str(e)}")
            return None, None
    else:
        st.warning("Veuillez importer un fichier au format CSV.")
        return None, None

# File uploader for tools data
def file_upload_tools():
    st.header("Importation des Outillages")
    tools_file = st.file_uploader("Importer les données des Outillages", type=["csv"], key="tools_upload")

    if tools_file is not None:
        try:
            tools_df = load_data(tools_file)

            if tools_df.empty or any(col not in tools_df.columns for col in ['Outillage', 'Disponibilité des outils']):
                st.error("Le fichier importé ne correspond pas au format attendu.")
                return None, None

            tools_input = tools_df['Outillage'].unique().tolist()
            tools_availability = tools_df.set_index('Outillage')['Disponibilité des outils'].to_dict()

            st.write("Données importées:")
            st.write(tools_df)

            return tools_input, tools_availability

        except Exception as e:
            st.error(f"Une erreur s'est produite lors du traitement du fichier : {str(e)}")
            return None, None
    else:
        st.warning("Veuillez importer un fichier au format CSV.")
        return None, None

# Function to upload task data
def file_upload_tasks():
    st.header("Importation des Tâches")
    tasks_file = st.file_uploader("Importer les données des Tâches", type=["csv"], key="tasks_upload")

    if tasks_file is not None:
        try:
            tasks_df = load_data(tasks_file)

            if tasks_df.empty or any(col not in tasks_df.columns for col in ['Tâche', 'Durée', 'Dépendances', 'Priorité']):
                st.error("Le fichier importé ne correspond pas au format attendu.")
                return None, None, None, None

            tasks_input = tasks_df['Tâche'].tolist()
            tasks_duration = tasks_df.set_index('Tâche')['Durée'].to_dict()
            dependencies = tasks_df.groupby('Tâche')['Dépendances'].apply(lambda x: [item for sublist in x.dropna().str.split(',').tolist() for item in sublist]).to_dict()
            task_priority = tasks_df.set_index('Tâche')['Priorité'].to_dict()

            st.write("Données importées:")
            st.write(tasks_df)

            return tasks_input, tasks_duration, dependencies, task_priority

        except Exception as e:
            st.error(f"Une erreur s'est produite lors du traitement du fichier : {str(e)}")
            return None, None, None, None
    else:
        st.warning("Veuillez importer un fichier au format CSV.")
        return None, None, None, None

# Function to optimize tasks
def optimize_tasks(tasks_input, tasks_duration, resources_input, resources_availability, tools_input, tools_availability, dependencies, task_priority):
    try:
        # Création du problème d'optimisation
        prob = LpProblem("Optimisation_Maintenance", LpMaximize)

        # Variables de décision: x[i][j] = 1 si la tâche i est assignée à RH j, 0 sinon
        x = LpVariable.dicts("assignement", ((i, j) for i in range(len(tasks_input)) for j in range(len(resources_input))), 0, 1, cat=LpBinary)

        # Fonction objectif: maximiser le nombre de tâches complétées
        prob += lpSum(x[i, j] * task_priority[tasks_input[i]] for i in range(len(tasks_input)) for j in range(len(resources_input))), "Nombre_de_taches_completees"

        # Contraintes: chaque tâche doit être assignée à un RH
        for i in range(len(tasks_input)):
            prob += lpSum(x[i, j] for j in range(len(resources_input))) == 1, f"Assignation_tache_{i}"

        # Contraintes: respect des disponibilités des RH
        for j in range(len(resources_input)):
            prob += lpSum(x[i, j] * tasks_duration[tasks_input[i]] for i in range(len(tasks_input))) <= resources_availability[resources_input[j]], f"Disponibilite_RH_{j}"

        # Contraintes: respect des disponibilités des outillages
        for o, tool in enumerate(tools_input):
            prob += lpSum(x[i, j] for i in range(len(tasks_input)) for j in range(len(resources_input))) <= tools_availability[tool], f"Disponibilite_outillage_{o}"

        # Contraintes: respect des dépendances des tâches
        constraint_id = 0
        for i, task in enumerate(tasks_input):
            if task in dependencies:
                for prereq in dependencies[task]:
                    if prereq in tasks_input:
                        prob += lpSum(x[tasks_input.index(prereq), j] for j in range(len(resources_input))) >= lpSum(x[i, j] for j in range(len(resources_input))), f"Contrainte_{i}_{tasks_input.index(prereq)}_{constraint_id}"
                        constraint_id += 1

        # Adding constraints to balance the workload between technicians
        max_hours = sum(tasks_duration.values())
        avg_hours = max_hours / len(resources_input)
        for j in range(len(resources_input)):
            prob += lpSum(x[i, j] * tasks_duration[tasks_input[i]] for i in range(len(tasks_input))) <= avg_hours + 2, f"Balanced_Workload_{j}"

        # Résolution du problème
        prob.solve()

        # Affichage des résultats
        st.subheader("Résultats")
        st.write(f"Status: {LpStatus[prob.status]}")
        results = []
        for i in range(len(tasks_input)):
            for j in range(len(resources_input)):
                if x[i, j].varValue == 1:
                    results.append({"Tâche": tasks_input[i], "Ressource Humaine": resources_input[j], "Durée": tasks_duration[tasks_input[i]]})
        result_df = pd.DataFrame(results)

        # Calculate start and finish times for each task
        start_times = {res: datetime.now() for res in resources_input}
        result_df['Start'] = result_df.apply(lambda row: start_times[row["Ressource Humaine"]], axis=1)
        result_df['Finish'] = result_df.apply(lambda row: (start_times[row["Ressource Humaine"]] + timedelta(hours=row["Durée"])), axis=1)

        # Update start times for each resource to ensure tasks are scheduled sequentially
        for res in resources_input:
            for index, row in result_df[result_df['Ressource Humaine'] == res].iterrows():
                result_df.at[index, 'Start'] = start_times[res]
                result_df.at[index, 'Finish'] = start_times[res] + timedelta(hours=row['Durée'])
                start_times[res] = result_df.at[index, 'Finish']

        st.write(result_df)

        # Affichage de la solution optimale
        st.subheader("Solution Optimale")
        for v in prob.variables():
            if v.varValue > 0:
                st.write(f"{v.name.replace('_', ' ')} = {v.varValue}")

        st.write(f"Valeur de la fonction objectif = {prob.objective.value()}")

        # Gantt Chart
        st.subheader("Diagramme de Gantt")
        if len(result_df) > 0:
            fig = px.timeline(result_df, x_start='Start', x_end='Finish', y='Ressource Humaine', color='Tâche', title="Diagramme de Gantt")
            fig.update_yaxes(categoryorder='total ascending')
            fig.update_layout(xaxis_title="Temps", yaxis_title="Ressources Humaines")
            st.plotly_chart(fig)
        else:
            st.write("Aucune donnée disponible pour afficher le diagramme de Gantt.")

    except Exception as e:
        st.error(f"Une erreur s'est produite: {str(e)}")
# Main application
data_upload_option = st.radio("Sélectionnez une option pour importer les données:", ["Manuel", "Importer un seul fichier", "Importer chaque fichier séparément"], key="data_upload_option")

if data_upload_option == "Manuel":
    tasks_input, tasks_duration, resources_input, resources_availability, tools_input, tools_availability, dependencies, task_priority = manual_input()

elif data_upload_option == "Importer un seul fichier":
    tasks_input, tasks_duration, resources_input, resources_availability, tools_input, tools_availability, dependencies, task_priority = file_upload_all()

else:
    tasks_input, tasks_duration, dependencies, task_priority = file_upload_tasks()
    resources_input, resources_availability = file_upload_resources()
    tools_input, tools_availability = file_upload_tools()

if st.button("Optimiser", key="optimize_button"):
    if tasks_input and resources_input and tools_input:
        optimize_tasks(tasks_input, tasks_duration, resources_input, resources_availability, tools_input, tools_availability, dependencies, task_priority)
    else:
        st.warning("Veuillez remplir toutes les informations nécessaires avant d'optimiser.")