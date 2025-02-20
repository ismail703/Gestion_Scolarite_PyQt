import sqlite3
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *

def connect_db():
    return sqlite3.connect("Gestion_Scolarite.db")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion Scolarité")
        self.setGeometry(100, 100, 800, 600)

        # Create a tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add tabs for each functionality
        self.tabs.addTab(Enseignant(), "Enseignants")
        self.tabs.addTab(Module(), "Modules")
        self.tabs.addTab(Etudiant(), "Etudiants")
        self.tabs.addTab(InscriptionApp(), "Inscriptions")

class Enseignant(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()
        self.nom_input = QLineEdit()
        self.prenom_input = QLineEdit()
        self.cin_input = QLineEdit()
        self.departement_input = QLineEdit()

        form_layout.addRow("Nom:", self.nom_input)
        form_layout.addRow("Prénom:", self.prenom_input)
        form_layout.addRow("CIN:", self.cin_input)
        form_layout.addRow("Département:", self.departement_input)
        layout.addLayout(form_layout)

        self.clear_btn = QPushButton("Effacer les Champs")
        self.clear_btn.setFixedWidth(150)
        self.clear_btn.clicked.connect(self.clear_inputs)

        self.add_btn = QPushButton("Ajouter Enseignant")
        self.add_btn.setFixedWidth(150)
        self.add_btn.clicked.connect(self.ajouter_enseignant)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.add_btn)
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Nom", "Prénom", "CIN", "Département", "Supprimer", "Modifier"])
        layout.addWidget(self.table)

        self.lister_enseignant()
        self.setLayout(layout)

    def ajouter_enseignant(self):
        nom = self.nom_input.text()
        prenom = self.prenom_input.text()
        cin = self.cin_input.text()
        departement = self.departement_input.text()

        if not nom or not prenom or not cin or not departement:
            QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis!")
            return

        try:
            conn = connect_db()
            curs = conn.cursor()
            curs.execute("INSERT INTO Enseignant (nom, prenom, cin, departement) VALUES (?, ?, ?, ?);", (nom, prenom, cin, departement))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Succès", "Enseignant ajouté avec succès!")
            self.clear_inputs()
            self.lister_enseignant()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def lister_enseignant(self):
        self.table.setRowCount(0)

        try:
            conn = connect_db()
            curs = conn.cursor()
            curs.execute("SELECT id, nom, prenom, cin, departement FROM Enseignant;")
            enseignants = curs.fetchall()
            conn.close()

            self.table.setRowCount(len(enseignants))
            for i, ens in enumerate(enseignants):
                for j, data in enumerate(ens[1:]):
                    self.table.setItem(i, j, QTableWidgetItem(str(data)))

                del_btn = QPushButton("Supprimer")
                del_btn.clicked.connect(lambda _, id=enseignants[i][0]: self.supprimer_enseignant(id))
                self.table.setCellWidget(i, 4, del_btn)

                update_btn = QPushButton("Modifier")
                update_btn.clicked.connect(lambda _, id=enseignants[i][0]: self.modifier_enseignant(id))
                self.table.setCellWidget(i, 5, update_btn)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def supprimer_enseignant(self, ens_id):
        try:
            conn = connect_db()
            curs = conn.cursor()
            curs.execute("DELETE FROM Enseignant WHERE id = ?", (ens_id,))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Succès", f"Enseignant avec l'id {ens_id} supprimé!")
            self.lister_enseignant()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def clear_inputs(self):
        self.nom_input.clear()
        self.prenom_input.clear()
        self.cin_input.clear()
        self.departement_input.clear()
        self.switch_ajout()

    def modifier_enseignant(self, ens_id):
        try:
            conn = connect_db()
            curs = conn.cursor()
            curs.execute("SELECT nom, prenom, cin, departement FROM Enseignant WHERE id = ?", (ens_id,))
            enseignant = curs.fetchone()
            conn.close()

            if enseignant:
                self.nom_input.setText(enseignant[0])
                self.prenom_input.setText(enseignant[1])
                self.cin_input.setText(enseignant[2])
                self.departement_input.setText(enseignant[3])

                self.add_btn.setText("Modifier Enseignant")
                self.add_btn.clicked.disconnect()
                self.add_btn.clicked.connect(lambda: self.applique_Modification(ens_id))
            else:
                QMessageBox.critical(self, "Erreur", f"Aucun enseignant trouvé avec l'id {ens_id}!")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def applique_Modification(self, ens_id):
        nom = self.nom_input.text()
        prenom = self.prenom_input.text()
        cin = self.cin_input.text()
        departement = self.departement_input.text()

        if not nom or not prenom or not cin or not departement:
            QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis!")
            return

        try:
            conn = connect_db()
            curs = conn.cursor()
            curs.execute("UPDATE Enseignant SET nom = ?, prenom = ?, cin = ?, departement = ? WHERE id = ?;", (nom, prenom, cin, departement, ens_id))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Succès", "Enseignant modifié avec succès!")
            self.clear_inputs()
            self.lister_enseignant()
            self.switch_ajout()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def switch_ajout(self):
        self.add_btn.setText("Ajouter Enseignant")
        self.add_btn.clicked.disconnect()
        self.add_btn.clicked.connect(self.ajouter_enseignant)

class Module(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()
        self.ens_id = QLineEdit()
        self.matiere = QLineEdit()
        self.semestre = QLineEdit()

        form_layout.addRow("Enseignant ID:", self.ens_id)
        form_layout.addRow("Matière:", self.matiere)
        form_layout.addRow("Semestre:", self.semestre)
        layout.addLayout(form_layout)

        self.clear_btn = QPushButton("Effacer les Champs")
        self.clear_btn.setFixedWidth(150)
        self.clear_btn.clicked.connect(self.clear_inputs)

        self.add_btn = QPushButton("Ajouter Module")
        self.add_btn.setFixedWidth(150)
        self.add_btn.clicked.connect(self.Ajouter_Module)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.add_btn)
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Enseignant ID", "Matière", "Semestre", "Supprimer", "Modifier"])
        layout.addWidget(self.table)

        self.Lister_Module()
        self.setLayout(layout)

    def Ajouter_Module(self):
        ens_id = self.ens_id.text()
        matiere = self.matiere.text()
        semestre = self.semestre.text()

        try:
            conn = connect_db()
            curs = conn.cursor()

            if not ens_id or not matiere or not semestre:
                QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis!")
                return

            curs.execute("SELECT 1 FROM Enseignant WHERE id = ?", (ens_id,))
            if not curs.fetchone():
                QMessageBox.warning(self, "Erreur", "L'enseignant avec cet ID n'existe pas!")
                return

            curs.execute("INSERT INTO Module (Enseignant_id, matiere, semestre) VALUES (?, ?, ?);", (ens_id, matiere, semestre))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Succès", "Module ajouté avec succès!")
            self.clear_inputs()
            self.Lister_Module()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def Lister_Module(self):
        self.table.setRowCount(0)

        try:
            conn = connect_db()
            curs = conn.cursor()
            curs.execute("SELECT * FROM Module;")
            modules = curs.fetchall()
            conn.close()

            self.table.setRowCount(len(modules))
            for i, module in enumerate(modules):
                for j, data in enumerate(module):
                    self.table.setItem(i, j, QTableWidgetItem(str(data)))

                del_btn = QPushButton("Supprimer")
                del_btn.clicked.connect(lambda _, id=module[0]: self.Sup_Module(id))
                self.table.setCellWidget(i, 4, del_btn)

                update_btn = QPushButton("Modifier")
                update_btn.clicked.connect(lambda _, id=module[0]: self.Modifier_Module(id))
                self.table.setCellWidget(i, 5, update_btn)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def Sup_Module(self, module_id):
        try:
            conn = connect_db()
            curs = conn.cursor()
            curs.execute("DELETE FROM Module WHERE id = ?", (module_id,))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Succès", f"Module avec l'id {module_id} supprimé!")
            self.Lister_Module()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def clear_inputs(self):
        self.ens_id.clear()
        self.matiere.clear()
        self.semestre.clear()
        self.switch_ajout()

    def Modifier_Module(self, module_id):
        try:
            conn = connect_db()
            curs = conn.cursor()
            curs.execute("SELECT Enseignant_id, matiere, semestre FROM Module WHERE id = ?", (module_id,))
            module = curs.fetchone()
            conn.close()

            if module:
                self.ens_id.setText(str(module[0]))
                self.matiere.setText(module[1])
                self.semestre.setText(module[2])

                self.add_btn.setText("Modifier module")
                self.add_btn.clicked.disconnect()
                self.add_btn.clicked.connect(lambda: self.Applique_Modification(module_id))
            else:
                QMessageBox.critical(self, "Erreur", f"Aucun module trouvé avec l'id {module_id}!")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def Applique_Modification(self, module_id):
        ens_id = self.ens_id.text()
        matiere = self.matiere.text()
        semestre = self.semestre.text()

        if not ens_id or not matiere or not semestre:
            QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis!")
            return

        try:
            conn = connect_db()
            curs = conn.cursor()
            curs.execute("UPDATE Module SET Enseignant_id = ?, matiere = ?, semestre = ? WHERE id = ?;", (ens_id, matiere, semestre, module_id))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Succès", "Module modifié avec succès!")
            self.clear_inputs()
            self.Lister_Module()
            self.switch_ajout()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def switch_ajout(self):
        self.add_btn.setText("Ajouter Module")
        self.add_btn.clicked.disconnect()
        self.add_btn.clicked.connect(self.Ajouter_Module)

class Etudiant(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion des Etudiants")
        self.setGeometry(300, 300, 700, 500)
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        # Main Layout
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # Form Layout
        form_layout = QFormLayout()
        self.num_apogee = QLineEdit()
        self.nom = QLineEdit()
        self.prenom = QLineEdit()
        self.cin = QLineEdit()
        self.date_naiss = QLineEdit()

        form_layout.addRow("Numero d'apogee:", self.num_apogee)
        form_layout.addRow("Nom:", self.nom)
        form_layout.addRow("Prenom:", self.prenom)
        form_layout.addRow("CIN:", self.cin)
        form_layout.addRow("date de naissance:", self.date_naiss)
        self.layout.addLayout(form_layout)

        # Buttons Layout
        self.clear_btn = QPushButton("Effacer les Champs")
        self.clear_btn.setFixedWidth(150)
        self.clear_btn.clicked.connect(self.clear_inputs)

        self.add_btn = QPushButton("Ajouter Module")
        self.add_btn.setFixedWidth(150)
        self.add_btn.clicked.connect(self.Ajouter_Etudiant)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.add_btn)
        self.layout.addLayout(button_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["Numero d'apogee", "Nom", "Prenom", "CIN", "Date de Naissance", "Supprimer", "Modifier"])
        self.layout.addWidget(self.table)

        self.Lister_Etudiant()

    def Ajouter_Etudiant(self):
        num_apogee = self.num_apogee.text()
        nom = self.nom.text()
        prenom = self.prenom.text()
        cin = self.cin.text()
        date_naiss = self.date_naiss.text()

        if not num_apogee or not nom or not prenom or not cin or not date_naiss:
            QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis!")
            return

        try:
            conn = connect_db()
            curs = conn.cursor()

            curs.execute("SELECT 1 FROM Etudiant WHERE num_apogee = ?", (num_apogee,))
            if curs.fetchone():
                QMessageBox.warning(self, "Erreur", "L'etudiant avec cet Apogee existe deja!")
                return

            curs.execute("""
                INSERT INTO Etudiant (num_apogee, nom, prenom, cin, date_naiss)
                VALUES (?, ?, ?, ?, ?);
            """, (num_apogee, nom, prenom, cin, date_naiss))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Succès", "Etudiant ajouté avec succès!")
            self.clear_inputs()  # Reset form fields after adding the student
            self.Lister_Etudiant()  # Refresh the student list
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def Lister_Etudiant(self):
        self.table.setRowCount(0)

        try:
            conn = connect_db()
            curs = conn.cursor()
            curs.execute("SELECT * FROM Etudiant;")
            etudiants = curs.fetchall()
            conn.close()

            self.table.setRowCount(len(etudiants))
            for i, etu in enumerate(etudiants):
                for j, data in enumerate(etu):
                    self.table.setItem(i, j, QTableWidgetItem(str(data)))

                # Delete Button
                del_btn = QPushButton("Supprimer")
                del_btn.clicked.connect(lambda _, id=etu[0]: self.Sup_Etudiant(id))
                self.table.setCellWidget(i, 5, del_btn)

                update_btn = QPushButton("Modifier")
                update_btn.clicked.connect(lambda _, id=etu[0]: self.Modifier_Etudiant(id))
                self.table.setCellWidget(i, 6, update_btn)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def Sup_Etudiant(self, etu_apogee):
        try:
            conn = connect_db()
            curs = conn.cursor()
            curs.execute("DELETE FROM Etudiant WHERE num_apogee = ?", (etu_apogee,))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Succès", f"Etudiant avec le numéro d'apogée {etu_apogee} supprimé!")
            self.Lister_Etudiant()  # Correct listing method
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def clear_inputs(self):
        self.num_apogee.clear()
        self.nom.clear()
        self.prenom.clear()
        self.cin.clear()
        self.date_naiss.clear()
        self.switch_ajout()

    def Modifier_Etudiant(self, etu_apogee):
        try:
            conn = connect_db()
            curs = conn.cursor()
            curs.execute("SELECT * FROM Etudiant WHERE num_apogee = ?", (etu_apogee,))
            etudiant = curs.fetchone()
            conn.close()

            if etudiant:
                self.nom.setText(etudiant[1])
                self.prenom.setText(etudiant[2])
                self.cin.setText(etudiant[3])
                self.date_naiss.setText(etudiant[4])

                self.add_btn.setText("Modifier Etudiant")
                self.add_btn.clicked.disconnect()
                self.add_btn.clicked.connect(lambda: self.Applique_Modification(etu_apogee))
            else:
                QMessageBox.critical(self, "Erreur", f"Aucun étudiant trouvé avec l'Apogée {etu_apogee}!")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def Applique_Modification(self, etu_apogee):
        num_apogee = self.num_apogee.text()
        nom = self.nom.text()
        prenom = self.prenom.text()
        cin = self.cin.text()
        date_naiss = self.date_naiss.text()

        if not num_apogee or not nom or not prenom or not cin or not date_naiss:
            QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis!")
            return

        try:
            conn = connect_db()
            curs = conn.cursor()
            curs.execute(""" UPDATE Etudiant
               SET nom = ?, prenom = ?, cin = ?, date_naiss = ?
               WHERE num_apogee = ?;""", (nom, prenom, cin, date_naiss, etu_apogee))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Succès", "Etudiant modifié avec succès!")
            self.clear_inputs()
            self.Lister_Etudiant()  # Correct the listing method for students

            self.switch_ajout()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def switch_ajout(self):
        self.add_btn.setText("Ajouter Module")
        self.add_btn.clicked.disconnect()
        self.add_btn.clicked.connect(self.Ajouter_Etudiant)

class InscriptionApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        form_layout = QFormLayout()
        self.module_id_input = QLineEdit()
        self.etudiant_apogee_input = QLineEdit()
        self.note_input = QLineEdit()
        self.valide_input = QLineEdit()

        form_layout.addRow("ID Module:", self.module_id_input)
        form_layout.addRow("Numéro Apogée:", self.etudiant_apogee_input)
        form_layout.addRow("Note:", self.note_input)
        form_layout.addRow("Validé:", self.valide_input)
        layout.addLayout(form_layout)

        self.clear_btn = QPushButton("Effacer les Champs")
        self.clear_btn.setFixedWidth(150)
        self.clear_btn.clicked.connect(self.clear_inputs)

        self.add_btn = QPushButton("Ajouter Inscription")
        self.add_btn.setFixedWidth(150)
        self.add_btn.clicked.connect(self.ajouter_inscription)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.add_btn)
        layout.addLayout(button_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID Module", "Numéro Apogée", "Note", "Validé", "Supprimer", "Modifier"])
        layout.addWidget(self.table)

        self.lister_inscriptions()
        self.setLayout(layout)

    def ajouter_inscription(self):
        module_id = self.module_id_input.text()
        etudiant_apogee = self.etudiant_apogee_input.text()
        note = self.note_input.text()
        valide = self.valide_input.text()

        if not module_id or not etudiant_apogee or not valide:
            QMessageBox.warning(self, "Erreur", "Tous les champs doivent être remplis!")
            return

        try:
            conn = connect_db()
            curs = conn.cursor()
            curs.execute("SELECT 1 FROM Module WHERE id = ?", (module_id,))
            if not curs.fetchone():
                QMessageBox.warning(self, "Erreur", "Le module avec cet ID n'existe pas!")
                return

            curs.execute("SELECT 1 FROM Etudiant WHERE num_apogee = ?", (etudiant_apogee,))
            if not curs.fetchone():
                QMessageBox.warning(self, "Erreur", "L'étudiant avec ce numéro d'apogée n'existe pas!")
                return

            curs.execute("INSERT INTO Inscrire (module_id, etudiant_apogee, note, valide) VALUES (?, ?, ?, ?);", (module_id, etudiant_apogee, note, valide))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Succès", "Inscription ajoutée avec succès!")
            self.clear_inputs()
            self.lister_inscriptions()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def lister_inscriptions(self):
        self.table.setRowCount(0)

        try:
            conn = connect_db()
            curs = conn.cursor()
            curs.execute("SELECT * FROM Inscrire;")
            inscriptions = curs.fetchall()
            conn.close()

            self.table.setRowCount(len(inscriptions))
            for i, insc in enumerate(inscriptions):
                for j, data in enumerate(insc):
                    self.table.setItem(i, j, QTableWidgetItem(str(data)))

                del_btn = QPushButton("Supprimer")
                del_btn.clicked.connect(lambda _, module_id=insc[0], etudiant_apogee=insc[1]: self.supprimer_inscription(module_id, etudiant_apogee))
                self.table.setCellWidget(i, 4, del_btn)

                mod_btn = QPushButton("Modifier")
                mod_btn.clicked.connect(lambda _, module_id=insc[0], etudiant_apogee=insc[1]: self.modifier_inscription(module_id, etudiant_apogee))
                self.table.setCellWidget(i, 5, mod_btn)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def supprimer_inscription(self, module_id, etudiant_apogee):
        try:
            conn = connect_db()
            curs = conn.cursor()
            curs.execute("DELETE FROM Inscrire WHERE module_id = ? AND etudiant_apogee = ?", (module_id, etudiant_apogee))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Succès", f"Inscription supprimée!")
            self.lister_inscriptions()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def modifier_inscription(self, module_id, etudiant_apogee):
        try:
            conn = connect_db()
            curs = conn.cursor()
            curs.execute("SELECT note, valide FROM Inscrire WHERE module_id = ? AND etudiant_apogee = ?", (module_id, etudiant_apogee))
            inscription = curs.fetchone()
            conn.close()

            if inscription:
                self.note_input.setText(str(inscription[0]))
                self.valide_input.setText(inscription[1])

                self.add_btn.setText("Modifier Inscription")
                self.add_btn.clicked.disconnect()
                self.add_btn.clicked.connect(lambda: self.applique_Modification(module_id, etudiant_apogee))
            else:
                QMessageBox.critical(self, "Erreur", f"Aucune inscription trouvée!")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def applique_Modification(self, module_id, etudiant_apogee):
        note = self.note_input.text()
        valide = self.valide_input.text()

        if not valide:
            QMessageBox.warning(self, "Erreur", "Le champ 'Validé' doit être rempli!")
            return

        try:
            conn = connect_db()
            curs = conn.cursor()
            curs.execute("UPDATE Inscrire SET note = ?, valide = ? WHERE module_id = ? AND etudiant_apogee = ?;", (note, valide, module_id, etudiant_apogee))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Succès", "Inscription modifiée avec succès!")
            self.clear_inputs()
            self.lister_inscriptions()
            self.add_btn.setText("Ajouter Inscription")
            self.add_btn.clicked.disconnect()
            self.add_btn.clicked.connect(self.ajouter_inscription)
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Erreur", f"Une erreur est survenue: {e}")

    def clear_inputs(self):
        self.module_id_input.clear()
        self.etudiant_apogee_input.clear()
        self.note_input.clear()
        self.valide_input.clear()

# Run the application
app = QApplication([])
window = MainWindow()
window.show()
app.exec()