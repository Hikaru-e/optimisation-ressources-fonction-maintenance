import streamlit as st
from pulp import LpMaximize, LpProblem, LpVariable, lpSum, LpStatus
import pandas as pd
import plotly.express as px

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
    task_rows = st.number_input("Nombre de Tâches", min_value=1, value=1, step=1)
    tasks_input = [st.text_input(f"Tâche {i+1}", key=f"task_input_{i}") for i in range(task_rows)]
    tasks_duration = {task: st.number_input(f"Durée de {task} (heures)", min_value=1, key=f"task_duration_{i}_{task}") for i, task in enumerate(tasks_input)}

    st.header("Saisie des Ressources Humaines")
    resource_rows = st.number_input("Nombre de Ressources Humaines", min_value=1, value=1, step=1)
    resources_input = [st.text_input(f"Ressource Humaine {i+1}", key=f"resource_input_{i}") for i in range(resource_rows)]
    resources_availability = {res: st.number_input(f"Disponibilité de {res} (heures)", min_value=1, key=f"resource_availability_{i}") for i, res in enumerate(resources_input)}

    st.header("Saisie des Outillages")
    tool_rows = st.number_input("Nombre d'Outillages", min_value=1, value=1, step=1)
    tools_input = [st.text_input(f"Outillage {i+1}", key=f"tool_input_{i}") for i in range(tool_rows)]
    tools_availability = {tool: st.number_input(f"Disponibilité de {tool} (heures)", min_value=1, key=f"tool_availability_{i}") for i, tool in enumerate(tools_input)}

    st.header("Dépendances des Tâches")
    dependencies = {}
    for i, task in enumerate(tasks_input):
        dependencies[task] = st.multiselect(f"Tâches prérequises pour {task}", tasks_input, key=f"dependencies_{i}_{task}")

    st.header("Priorité des Tâches")
    task_priority = {f"{task}_{i}": st.slider(f"Priorité de {task}", min_value=1, max_value=10, value=5, key=f"priority_{task}_{i}") for i, task in enumerate(tasks_input)}

    return tasks_input, tasks_duration, resources_input, resources_availability, tools_input, tools_availability, dependencies, task_priority

# File uploader for all data
def file_upload_all():
    st.header("Importation des Données")
    all_data_file = st.file_uploader("Importer toutes les données (tâches, ressources et outils)", type=["csv"])

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

            dependencies = all_data_df.groupby('Tâche')['Dépendances'].apply(lambda x: x.unique().tolist()).to_dict()
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
    resources_file = st.file_uploader("Importer les données des Ressources Humaines", type=["csv"])

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
    tools_file = st.file_uploader("Importer les données des Outillages", type=["csv"])

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

# Function to optimize tasks
def optimize_tasks(tasks_input, tasks_duration, resources_input, resources_availability, tools_input, tools_availability, dependencies, task_priority):
    try:
        # Création du problème d'optimisation
        prob = LpProblem("Optimisation_Maintenance", LpMaximize)

        # Variables de décision: x[i][j] = 1 si la tâche i est assignée à RH j, 0 sinon
        x = LpVariable.dicts("assignement", ((i, j) for i in tasks_input for j in resources_input), 0, 1, cat='Binary')

        # Fonction objectif: maximiser le nombre de tâches complétées
        prob += lpSum(x[i, j] * task_priority[f"{i}_{tasks_input.index(i)}"] for i in tasks_input for j in resources_input), "Nombre_de_taches_completees"

        # Contraintes: chaque tâche doit être assignée à un RH
        for i in tasks_input:
            prob += lpSum(x[i, j] for j in resources_input) == 1, f"Assignation_tache_{i}"

        # Contraintes: respect des disponibilités des RH
        for j in resources_input:
            prob += lpSum(x[i, j] * tasks_duration[i] for i in tasks_input) <= resources_availability[j], f"Disponibilite_RH_{j}"

        # Contraintes: respect des disponibilités des outillages
        for o in tools_input:
            prob += lpSum(x[i, j] for i in tasks_input for j in resources_input) <= tools_availability[o], f"Disponibilite_outillage_{o}"

        # Contraintes: respect des dépendances des tâches
        for task, prereqs in dependencies.items():
            for prereq in prereqs:
                prob += lpSum(x[prereq, j] for j in resources_input) <= lpSum(x[task, j] for j in resources_input), f"Contrainte_{task}_{prereq}"

        # Résolution du problème
        prob.solve()

        # Affichage des résultats
        st.subheader("Résultats")
        st.write(f"Status: {LpStatus[prob.status]}")
        results = []
        for i in tasks_input:
            for j in resources_input:
                if x[i, j].varValue == 1:
                    results.append({"Tâche": i, "Ressource Humaine": j})
        result_df = pd.DataFrame(results)

        # Convert task duration to datetime format and calculate finish time
        result_df['Start'] = pd.to_datetime('now').strftime('%Y-%m-%d %H:%M:%S')
        result_df['Finish'] = result_df.apply(lambda row: (pd.to_datetime('now') + pd.Timedelta(hours=tasks_duration[row["Tâche"]])).strftime('%Y-%m-%d %H:%M:%S'), axis=1)

        st.write(result_df)

        # Affichage de la solution optimale
        st.subheader("Solution Optimale")
        for v in prob.variables():
            st.write(f"{v.name} = {v.varValue}")

        st.write(f"Valeur de la fonction objectif = {prob.objective.value()}")

        # Gantt Chart
        st.subheader("Diagramme de Gantt")
        if len(result_df) > 0:
            fig = px.timeline(result_df, x_start='Start', x_end='Finish', y='Ressource Humaine', title="Diagramme de Gantt")
            fig.update_yaxes(categoryorder='total ascending')
            fig.update_layout(xaxis_title="Tâches", yaxis_title="Ressources Humaines")
            st.plotly_chart(fig)
        else:
            st.write("Aucune donnée disponible pour afficher le diagramme de Gantt.")

    except Exception as e:
        st.error(f"Une erreur s'est produite: {str(e)}")

# Main application
data_upload_option = st.radio("Sélectionnez une option pour importer les données:", ["Manuel", "Importer un seul fichier", "Importer chaque fichier séparément"])

if data_upload_option == "Manuel":
    tasks_input, tasks_duration, resources_input, resources_availability, tools_input, tools_availability, dependencies, task_priority = manual_input()

elif data_upload_option == "Importer un seul fichier":
    tasks_input, tasks_duration, resources_input, resources_availability, tools_input, tools_availability, dependencies, task_priority = file_upload_all()

else:
    resources_input, resources_availability = file_upload_resources()
    tools_input, tools_availability = file_upload_tools()
    tasks_input, tasks_duration, _, _, _, _, dependencies, task_priority = file_upload_all()

if st.button("Optimiser"):
    if tasks_input and resources_input and tools_input:
        optimize_tasks(tasks_input, tasks_duration, resources_input, resources_availability, tools_input, tools_availability, dependencies, task_priority)
    else:
        st.warning("Veuillez remplir toutes les informations nécessaires avant d'optimiser.")
