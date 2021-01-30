import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import re
import matplotlib as mpl
from functools import partial
from algos import *

# (classe, dimensions) : (numéro salle, (point initial))
# classesSallesLV1 = {('A', (108, 136)): (1001, (31, 32)), ('G', (102, 112)): (1019, (567, 221))}
# classesCouloirs = {('A', (94, 38)): [(1003, (238, 187)), (1005, (421, 187)), (1006, (515, 187)), (1008, (685, 187)),
#                                     (1020, (669, 187))]}

# classesVal = {1: (94, 25), 2: (170, 28), 3: (28, 106), 4: (24, 79),
# 5: (24, 40), 6: (75, 25), 7: (100, 30), 8: (50, 18)}
# salles = np.concatenate((np.arange(1001, 1026), np.arange(2001, 2041), np.arange(3001, 3076)))
# salles = np.array([1003, 1005, 1006, 1008, 1020, 1021, 1016, 1011, 1012, 1002,
#                   1009,
#                   1013, 1014,
#                   1018,
#                   1017,
#                   1007, 1004,
#                   1019, 2003, 2005, 2006,
#                   2002])
# coul_X = np.array([238, 421, 515, 685, 669, 771, 1033, 953, 1046, 144,
#                   781,
#                   1145, 1145,
#                   1046,
#                   1046,
#                   609, 340,
#                   565, 237, 420, 515,
#                   140])
# coul_Y = np.concatenate([np.repeat(187, 6), np.array([345, 145, 145, 145,
#                                                      147,
#                                                      149, 259,
#                                                      219,
#                                                      301,
#                                                      187, 187,
#                                                      187, 188, 188, 188,
#                                                      150])])
# classes = np.concatenate([np.repeat(1, 10), np.array([2, 3, 3, 4, 5, 6, 6, 7, 7, 7, 7, 8])])

# classesCouloirs = pd.DataFrame({'Salle': salles, 'X': coul_X, 'Y': coul_Y, 'Classe': classes})

# 1: Salle de bain
# 2: Commodités
# 3: Salon
# 4: Chambre 1
# 5: Chambre 2
# 6: Cuisine
# 7: Couloir
# ((point origine), (longueur, largeur))
salletype_backup = {1: ((715, 405), (134, 138)), 2: ((595, 405), (114, 138)), 3: ((10, 224), (464, 322)),
                    4: ((10, 551), (464, 292)), 5: ((480, 10), (370, 162)), 6: ((548, 178), (300, 220)),
                    7: ((480, 178), (62, 366))}

salletype = {1: ((515, 292), (97, 100)), 2: ((429, 292), (83, 100)), 3: ((7, 162), (334, 230)),
             4: ((7, 397), (334, 210)), 5: ((345, 7), (268, 117)), 6: ((396, 128), (217, 160)),
             7: ((345, 126), (46, 166))}

matadj = {1: 6, 2: 7, 3: (4, 7), 4: 3, 5: 7, 6: (1, 7), 7: (2, 3, 5, 6)}

matadj2 = {1: [6], 3: [4, 7], 4: [3], 5: [7], 6: [1, 7], 7: [3, 5, 6]}

temp_opt = 20

humid_opt = 40


class Interface:

    def __init__(self, fenetre, path, pathC):
        self.path = path
        self.pathC = pathC
        self.cpt = 0
        self.source = Image.open(pathC[0])
        # self.source.convert("RGBA")
        self.fenetre = fenetre
        self.fenetre.title("Pollution de l'air")
        self.fenetre.config(background="white")

        self.frame_image = tk.Frame(self.fenetre)
        self.frame_image.pack(side="bottom")
        self.frame_button = tk.Frame(self.fenetre)
        self.frame_button.pack(side="top")
        self.frame_button.config(bg="white")

        self.width = 1000
        self.height = 650

        self.cv = tk.Canvas(self.frame_image, width=self.width, height=self.height, bd=0,
                            highlightthickness=0, bg="white")
        self.photo = ImageTk.PhotoImage(self.source)
        self.image_on_canvas = self.cv.create_image(self.width / 2, self.height / 2, image=self.photo, anchor='center')
        self.cv.pack(side="top")

        self.listeData = []
        self.listeFiles = os.listdir("./data/")
        self.listeDates = []

        for e in self.listeFiles:
            if e == 'SG':
                continue
            self.searchName = re.search(r"([0-9]+-[0-9]+)_[0-9]+\.\w+", e)
            if self.searchName.group(1) not in self.listeDates:
                self.listeDates.append(self.searchName.group(1))
            self.tmp_file = pd.read_csv("./data/" + e, sep=';')
            self.tmp_file = self.tmp_file.dropna(axis='rows')
            self.tmp_file.loc[self.tmp_file['Particules'] <= 0.62, 'Particules'] = np.nan

            self.tmp_file.iloc[:, [7, 8, 10, 11]] = self.tmp_file.iloc[:, [7, 8, 10, 11]].apply(self.__mask, axis=0)

            self.tmp_file = self.tmp_file.reset_index(drop=True)
            self.tmp_listval = self.tmp_file.iloc[0, 0:7]
            self.tmp_listval = self.tmp_listval.append(self.tmp_file.iloc[:, 7:12].mean(skipna=True))
            self.listeData.append(self.tmp_listval)

        self.listeData = pd.DataFrame(self.listeData,
                                      columns=['Jour', 'Mois', 'Heure', 'Minutes', 'Secondes', 'Lieu',
                                               'Couloir', 'Temperature', 'Humidite', 'Particules',
                                               'Qualite', 'Son'])
        self.listeData['Couloir'] = self.listeData['Couloir'].astype(bool)
        self.listeData[['Jour', 'Mois', 'Heure', 'Minutes', 'Secondes', 'Lieu']] = \
            self.listeData[['Jour', 'Mois', 'Heure', 'Minutes', 'Secondes', 'Lieu']].astype(np.int32)
        self.listeData[['Temperature', 'Humidite', 'Particules', 'Qualite', 'Son']] = \
            self.listeData[['Temperature', 'Humidite', 'Particules', 'Qualite', 'Son']].astype(np.float64)

        self.listeData['Index'] = self.listeData.apply(lambda row: self.__get_index(row['Jour'], row['Mois']), axis=1)

        print(self.listeData.to_string())

        self.current_data = pd.DataFrame()
        self.icons = []
        self.__generate_icons()

        self.labelIndDate = ttk.Label(self.frame_button, text='Date : ')
        self.labelIndDate.grid(row=1, column=4)

        self.entereddate = tk.StringVar()
        self.choixDate = ttk.Entry(self.frame_button, textvariable=self.entereddate, width=10)
        self.choixDate.grid(row=1, column=5)

        tk.Button(self.frame_button, command=self.affiche_init, image=self.icons[4],
                  highlightthickness=0, bd=0, bg="white") \
            .grid(row=1, column=6)

        self.choixCol = ttk.Combobox(self.frame_button, state='readonly', width=12,
                                     values=['Temperature', 'Humidite', 'Particules', 'Qualite', 'Son'])
        self.choixCol.grid(row=1, column=7)

        tk.Button(self.frame_button, command=self.affiche_prec, image=self.icons[2],
                  highlightthickness=0, bd=0, bg="white") \
            .grid(row=1, column=1)
        tk.Button(self.frame_button, command=self.affiche_suiv, image=self.icons[3],
                  highlightthickness=0, bd=0, bg="white") \
            .grid(row=1, column=3)
        self.cb = ttk.Combobox(self.frame_button, values=list(range(1, len(names) + 1)),
                               state="readonly", height=3, width=7)

        self.cb.set("1")
        self.cb.grid(row=1, column=2)
        self.cb.bind("<<ComboboxSelected>>", self.affiche_num)

        tk.Button(self.frame_button, command=self.affiche_donnees, image=self.icons[0],
                  highlightthickness=0, bd=0, bg="white") \
            .grid(row=1, column=8)

        self.labelInit = ttk.Label(self.frame_button, text='Salle initiale')
        self.labelDest = ttk.Label(self.frame_button, text='Salle destination')
        self.labelInit.grid(row=2, column=1)
        self.labelDest.grid(row=2, column=3)
        self.choixInit = ttk.Combobox(self.frame_button, values=list(range(1, len(salletype) + 1)),
                                      state="readonly", height=3, width=7)
        self.choixInit.grid(row=2, column=2)

        self.choixDest = ttk.Combobox(self.frame_button, values=list(range(1, len(salletype) + 1)),
                                      state="readonly", height=3, width=7)
        self.choixDest.grid(row=2, column=4)

        tk.Button(self.frame_button, command=self.affiche_chemin, image=self.icons[1],
                  highlightthickness=0, bd=0, bg="white") \
            .grid(row=2, column=5)

    def __mask(self, serie):
        """
        filtre les donnees trop decalees de la moyenne/ecart-type
        :param serie: donnees d'un attribut
        :return: les donnees coherentes pour l'attribut
        """
        m = serie.mean()
        sd = serie.std()*4
        return serie.where(serie.between(m-sd, m+sd))

    def __changer_image(self, im):
        """
        procede au changement d'image affichée selon l'image fournie
        :param im: l'image à afficher
        :return: None
        """
        self.photo = ImageTk.PhotoImage(im)
        # cv.pack(side="top", fill="both", expand="yes")
        self.cv.itemconfig(self.image_on_canvas, image=self.photo)
        # self.cv.pack(side="top")

    def __generate_icons(self):
        """
        genere les images des icônes à affecter aux boutons
        :return: None
        """
        tab = ["./Images/eye.jpg", "./Images/road.jpg", "./Images/back.jpg",
               "./Images/next.jpg", "./Images/reload.jpg"]
        for path in tab:
            im = Image.open(path)
            im = im.resize((65, 65), Image.ANTIALIAS)
            self.icons.append(ImageTk.PhotoImage(im))

    @staticmethod
    def __get_index(jour, mois):
        """
        determine un index pour un jour et un mois donnes
        :param jour: entier entre 1 et 31 donnant le jour
        :param mois: entier entre 4 et 6 donnant le mois
        :return: l'index voulu
        """
        # En commençant au 11/04
        index = jour - 10
        if mois == 4:
            return index
        index = 20
        if mois == 5:
            return index + jour
        for i in range(6, 9):
            if i % 2 == 0:
                index += 31
            else:
                index += 30
            if i == mois:
                return index + jour
        for i in range(9, 12):
            if i % 2 == 0:
                index += 30
            else:
                index += 31
            if i == mois:
                return index + jour
        return None

    @staticmethod
    def __get_jour_mois(index):
        """
        determine le jour et le mois pour un index donne
        :param index: entier correspondant a l'index de la date recherchee
        :return: le jour et le mois correspondant a l'index
        """
        # En commençant au 11/04
        if index <= 20:
            return index + 10, 4
        if index <= 51:
            return index - 20, 5
        mois = 6
        tmp = 51
        while True:
            if mois < 8:
                if mois % 2 == 0:
                    if index <= tmp + 30:
                        return index - tmp, mois
                    tmp += 30
                    mois += 1
                else:
                    if index <= tmp + 31:
                        return index - tmp, mois
                    tmp += 31
                    mois += 1
            else:
                if mois % 2 == 0:
                    if index <= tmp + 31:
                        return index - tmp, mois
                    tmp += 31
                    mois += 1
                else:
                    if index <= tmp + 30:
                        return index - tmp, mois
                    tmp += 30
                    mois += 1
            if mois == 13:
                mois = 1

    @staticmethod
    def __color_fader(c1, c2, mix):  # fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
        """
        permet d'avoir les bonnes couleurs pour les degrades
        :param c1: premiere couleur
        :param c2: deuxieme couleur
        :param mix: écart entre les deux couleurs
        :return: hex de la couleur voulue
        """
        c1 = np.array(mpl.colors.to_rgb(c1))
        c2 = np.array(mpl.colors.to_rgb(c2))
        return mpl.colors.to_hex((1 - mix) * c1 + mix * c2)

    def __couleur_image(self, e, im, front):
        """
        affiche la couleur associee à une salle
        :param e: la salle
        :param im: l'image du plan
        :param front: l'image de la coloration
        :return: None
        """
        x = salletype[e][0][0]
        y = salletype[e][0][1]
        dimimage = (x, y, x + salletype[e][1][0], y + salletype[e][1][1])
        im.paste(front, dimimage, mask=front)

    def __predict_data(self, data, jour, mois, col, perc):
        """
        genere une valeur pour une date et une colonne donnees
        :param data: base de données pour le jour et le mois deja obtenue precedemment
        :param jour: entier entre 1 et 31 donnant le jour
        :param mois: entier entre 4 et 6 donnant le mois
        :param col: un nom d'une colonne de la DataFrame
        :param perc: boolean pour choisir la prediction par perceptron si True
        :return: une valeur pour la colonne et la date donnee
        """
        index = self.__get_index(jour, mois)
        if perc:
            p = percMulti(self.listeData, col)
            for e in salletype:
                df = self.listeData.loc[self.listeData.Lieu == e]
                if df.empty or not data.loc[data.Lieu == e].empty:
                    continue
                # prediction de la classe
                tmp = p.predict({'Lieu': e, 'weekday': pd.Timestamp(2020, mois, jour).dayofweek, 'Heure': 10})
                # valeur moyenne pour cette classe
                tmp = p.getAttVal(tmp)
                data = data.append(pd.DataFrame([[jour, mois, 0, 0, 0, e, 0, tmp, index]],
                                                columns=['Jour', 'Mois', 'Heure', 'Minutes',
                                                         'Secondes', 'Lieu', 'Couloir', col, 'Index']),
                                   ignore_index=True)
        else:
            for e in salletype:
                df = self.listeData.loc[self.listeData.Lieu == e]
                if df.empty or not data.loc[data.Lieu == e].empty:
                    continue
                df = df[['Index', col]]
                if linea_deter(df) < poly_deter(df):
                    tmp = regress_poly(df, [index])[0]
                else:
                    tmp = regress_linea(df, [index])[0]
                data = data.append(pd.DataFrame([[jour, mois, 0, 0, 0, e, 0, tmp, index]],
                                                columns=['Jour', 'Mois', 'Heure', 'Minutes',
                                                         'Secondes', 'Lieu', 'Couloir', col, 'Index']),
                                   ignore_index=True)

        return data

    def __check_date(self):
        """
        verifie si la date entree dans le champs prevu a cet effet est au bon format et convertit les valeurs en entiers
        :return: le mois et le jour de la date donnee
        """
        datesearch = re.search(r"([0-9][0-9]?-[0-9][0-9]?)", self.entereddate.get())
        if not datesearch:
            self.entereddate.set('')
            return
        mois, jour = datesearch.group(1).split('-')
        mois = int(mois)
        jour = int(jour)
        if mois < 4 or (jour < 11 and mois == 4):
            return
        return mois, jour

    def __affect_current_data(self, col, jour, mois):
        """
        decide de la methode a utiliser pour la prediction
        :param col: attribut a predire
        :param jour: entier entre 1 et 31 donnant le jour
        :param mois: entier entre 4 et 6 donnant le mois
        :return: None
        """
        if self.current_data.empty or self.current_data[col].isna().any() or \
                (self.current_data.iloc[0].Jour != jour or self.current_data.iloc[0].Mois != mois):
            self.current_data = self.listeData.loc[(self.listeData.Mois == mois) & (self.listeData.Jour == jour)].copy()

        if self.current_data.shape[0] < 6:
            if mois > self.listeData.Mois.max() or (jour > self.listeData[self.listeData.Mois == mois].Jour.max()
                                                    and mois == self.listeData.Mois.max()):
                self.current_data = self.__predict_data(self.current_data, jour, mois, col, True)
            else:
                self.current_data = self.__predict_data(self.current_data, jour, mois, col, False)

    def affiche_donnees(self):
        """
        colore le plan par rapport aux données selon la colonne, les salles et la date
        :return: None
        """
        # im = self.source.copy()
        date = self.__check_date()
        if date is None:
            return
        mois, jour = date

        col = self.choixCol.get()
        if not col:
            return

        im = Image.open(self.path[self.cpt])
        legim = Image.open('./Images/legende.jpg')
        im.paste(legim, (360, 500))

        self.__affect_current_data(col, jour, mois)
        data = self.current_data.copy()

        if col == 'Temperature':
            data[col] = abs(data[col] - temp_opt)
        elif col == 'Humidite':
            data[col] = abs(data[col] - humid_opt)
        data = data.sort_values(by=[col])
        nbr = len(data[col].unique())

        lcolor = []
        x = 0
        if nbr == 1:
            lcolor = [mpl.colors.to_hex('yellow')] * data.shape[0]
        else:
            for i in range(data.shape[0]):
                if i >= 1 and data.iloc[i][col] != data.iloc[i - 1][col]:
                    x += 1
                lcolor.append(self.__color_fader('yellow', 'purple', x / (nbr - 1)))
        data['Couleur'] = lcolor

        for i in range(data.shape[0]):
            salle = data.iloc[i]['Lieu']
            for e in salletype:
                if e == salle:
                    color = data.iloc[i]['Couleur']
                    front = Image.new("RGBA", salletype[e][1], color + '99')
                    self.__couleur_image(e, im, front)
        self.__changer_image(im)

    def __solution_valide(self, fr):
        """
        cherche un chemin optimal dans la frontière: si la destination est dans une des salles dans
        la frontiere et si son coût est minimal.
        :param fr: la fonctière avec les salles suivantes a évaluer
        :return: id du chemin optimal dans la frontiere ou -1 sinon
        """
        dest = int(self.choixDest.get())
        idres = -1
        minv = float("inf")
        for i in range(len(fr)):
            if minv > fr[i][1]:
                if fr[i][0][-1] == dest:
                    idres = i
                else:
                    idres = -1
                minv = fr[i][1]
            elif (minv == fr[i][1]) and (fr[i][0][-1] == dest):
                idres = i
        return idres

    def __new_voisins(self, fr, col):
        """
        cherche une salle dans la frontiere avec le coût de parcours le moins eleve
        et le remplace par ses voisins sans revenir sur ses pas.
        :param fr: la fonctière avec les salles suivantes à évaluer
        :param col: attribut etudiee
        :return: None
        """
        idm = -1
        opt = -1
        minv = float("inf")
        for i in range(len(fr)):
            if minv > fr[i][1]:
                minv = fr[i][1]
                idm = i
        tmp1 = set(matadj2[fr[idm][0][-1]])
        tmp2 = set(fr[idm][0])
        vois = list(tmp1 - tmp2)

        if col == 'Temperature':
            opt = temp_opt
        elif col == 'Humidite':
            opt = humid_opt
        if opt != -1:
            for v in vois:
                fr.append(
                    (fr[idm][0] + [v], fr[idm][1] +
                     abs(self.current_data.loc[self.current_data.Lieu == v][col].iloc[0] - opt)))
        else:
            for v in vois:
                fr.append(
                    (fr[idm][0] + [v], fr[idm][1] + self.current_data.loc[self.current_data.Lieu == v][col].iloc[0]))
        del fr[idm]

    def affiche_chemin(self):
        """
        affiche le chemin optimal selon un départ, une destination et
        un attribut environnemental
        :return: None
        """
        # im = self.source.copy()
        if (self.choixInit.get() == '') or (self.choixDest.get() == ''):
            print("Choisissez un départ et une destination")
            return

        date = self.__check_date()
        if date is None:
            return
        mois, jour = date

        col = self.choixCol.get()
        if not col:
            return

        self.__affect_current_data(col, jour, mois)

        im = Image.open(self.path[self.cpt])
        frontiere = [([int(self.choixInit.get())], 0)]
        self.__new_voisins(frontiere, col)
        loop = 0
        while len(frontiere) != 0:
            print("Iteration : " + str(loop))
            print(frontiere)
            id = self.__solution_valide(frontiere)
            if id != -1:
                path = frontiere[id]
                break
            self.__new_voisins(frontiere, col)
            loop += 1

        if len(frontiere) == 0:
            print("Chemin non trouvé")
            return
        path = frontiere[id][0]
        for i in range(len(path)):
            salle = path[i]
            for e in salletype:
                if e == salle:
                    print('path  ', salle)
                    front = Image.new("RGBA", salletype[e][1], "#00FF00" + '99')
                    self.__couleur_image(e, im, front)
        self.__changer_image(im)

    def affiche_prec(self):
        """
        organise l'affichage de l'etage precedent s'il existe
        :return: None
        """
        if self.cpt < 1:
            return
        self.cpt -= 1
        im = Image.open(self.pathC[self.cpt])
        # self.source = im
        self.cb.set(self.cpt + 1)
        self.__changer_image(im)

    def affiche_suiv(self):
        """
        organise l'affichage de l'etage suivant s'il existe
        :return: None
        """
        if self.cpt >= len(self.path) - 1:
            return
        self.cpt += 1
        im = Image.open(self.pathC[self.cpt])
        # self.source = im
        self.cb.set(self.cpt + 1)
        self.__changer_image(im)

    def affiche_init(self):
        """
        reinitialise l'image du plan pour effacer les informations affichees
        :return: None
        """
        self.__changer_image(Image.open(self.pathC[self.cpt]))

    def affiche_num(self, event):
        """
        organise l'affichage de l'etage lors d'une selection dans la liste deroulante
        :param event: la selection (a ne pas enlever !!!)
        :return: None
        """
        i = int(self.cb.get()) - 1
        im = Image.open(self.pathC[i])
        self.cpt = i
        self.__changer_image(im)


if __name__ == '__main__':
    fenetre = tk.Tk()
    # names = ["./Images/1.png", "./Images/2.png", "./Images/3.png", "./Images/4.png",
    #         "./Images/5.png", "./Images/6.png", "./Images/7.png", "./Images/8.png"]

    # namesC = ["./Images/1C.png", "./Images/2C.png", "./Images/3C.png", "./Images/4C.png",
    #          "./Images/5C.png", "./Images/6C.png", "./Images/7C.png", "./Images/8C.png"]

    names = ["./Images/PlanAppartement_min.png"]

    namesC = ["./Images/PlanAppartement_min.png"]

    Interface(fenetre, names, namesC)

    fenetre.mainloop()
