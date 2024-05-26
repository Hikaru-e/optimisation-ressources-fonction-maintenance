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

# Saisie des tâches
st.header("Saisie des Tâches")
task_rows = st.number_input("Nombre de Tâches", min_value=1, value=1, step=1)
tasks_input = [st.text_input(f"Tâche {i+1}", key=f"task_input_{i}") for i in range(task_rows)]
tasks_duration = {task: st.number_input(f"Durée de {task} (heures)", min_value=1, key=f"task_duration_{i}_{task}") for i, task in enumerate(tasks_input)}

# Saisie des ressources humaines
st.header("Saisie des Ressources Humaines")
resource_rows = st.number_input("Nombre de Ressources Humaines", min_value=1, value=1, step=1)
resources_input = [st.text_input(f"Ressource Humaine {i+1}", key=f"resource_input_{i}") for i in range(resource_rows)]
resources_availability = {res: st.number_input(f"Disponibilité de {res} (heures)", min_value=1, key=f"resource_availability_{i}") for i, res in enumerate(resources_input)}

# Saisie des outillages
st.header("Saisie des Outillages")
tool_rows = st.number_input("Nombre d'Outillages", min_value=1, value=1, step=1)
tools_input = [st.text_input(f"Outillage {i+1}", key=f"tool_input_{i}") for i in range(tool_rows)]
tools_availability = {tool: st.number_input(f"Disponibilité de {tool} (heures)", min_value=1, key=f"tool_availability_{i}") for i, tool in enumerate(tools_input)}

# Tâches et dépendances
st.header("Dépendances des Tâches")
dependencies = {}
for i, task in enumerate(tasks_input):
    dependencies[task] = st.multiselect(f"Tâches prérequises pour {task}", tasks_input, key=f"dependencies_{i}_{task}")

# Priorité des tâches
st.header("Priorité des Tâches")
task_priority = {f"{task}_{i}": st.slider(f"Priorité de {task}", min_value=1, max_value=10, value=5, key=f"priority_{task}_{i}") for i, task in enumerate(tasks_input)}

# Bouton pour lancer l'optimisation
if st.button("Optimiser"):
    try:
        # Création du problème d'optimisation
        prob = LpProblem("Optimisation_Maintenance", LpMaximize)

        # Variables de décision: x[i][j] = 1 si la tâche i est assignée à RH j, 0 sinon
        x = LpVariable.dicts("assignement", ((i, j) for i in tasks_input for j in resources_input), 0, 1, cat='Binary')

        # Fonction objectif: maximiser le nombre de tâches complétées
        prob += lpSum(x[i, j] * task_priority[i] for i in tasks_input for j in resources_input), "Nombre_de_taches_completees"

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
        result_df['Finish'] = result_df.apply(lambda row: (pd.to_datetime('now') + pd.Timedelta(hours=tasks_duration[row["Tâche"]])) .strftime('%Y-%m-%d %H:%M:%S'), axis=1)

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
