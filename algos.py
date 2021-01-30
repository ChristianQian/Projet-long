import numpy as np
import pandas as pd
import random


def coef_poly(df):
    """
    calcule les coefficients et la constante de la fonction de regression quadratique
    :param df: DataFrame a deux colonnes contenant les données a étudier
    :return: liste avec es coefficients et la constante
    """
    if df.shape[1] != 2:
        return
    df.columns = ['X', 'Y']
    sx = df.X.sum()
    sx2 = np.square(df.X).sum()
    sx3 = np.power(df.X, 3).sum()
    values = np.array([df.Y.sum(), df.prod(axis=1).sum(), np.square(df.X).multiply(df.Y).sum()])
    coefs = np.array([[df.shape[0], sx, sx2],
                      [sx, sx2, sx3],
                      [sx2, sx3, np.power(df.X, 4).sum()]])
    return np.linalg.solve(coefs, values)


def coef_linea(df):
    """
    calcule le coefficient et la constante de la fonction de regression lineaire
    :param df: DataFrame a deux colonnes contenant les données a étudier
    :return: liste avec le coefficient et la constante
    """
    if df.shape[1] != 2:
        return
    df.columns = ['X', 'Y']
    a = df.cov().X.iloc[1] / df.X.var()
    b = df.Y.mean() - a * df.X.mean()
    return [b, a]


def regress_poly(df, X):
    """
    determine une image pour chaque valeur en abscisse donnee en utilisant la regression quadratique
    :param df: DataFrame a deux colonnes contenant les donnees connues
    :param X: liste des abscisses pour lesquelles on veut une image
    :return: liste des images recherchees
    """
    if df.shape[1] != 2:
        return
    df.columns = ['X', 'Y']
    res = coef_poly(df)
    return list(map(lambda x: res[0] + res[1] * x + res[2] * x ** 2, X))


def regress_linea(df, X):
    """
    determine une image pour chaque valeur en abscisse donnee en utilisant la regression lineaire
    :param df: DataFrame a deux colonnes contenant les donnees connues
    :param X: liste des abscisses pour lesquelles on veut une image
    :return: liste des images recherchées
    """
    if df.shape[1] != 2:
        return
    df.columns = ['X', 'Y']
    res = coef_linea(df)
    return list(map(lambda x: res[0] + res[1] * x, X))


def linea_deter(df):
    """
    determine le coefficient de determination pour la regression lineaire
    :param df: DataFrame a deux colonnes contenant les donnees a etudier
    :return: le coefficient de determination
    """
    if df.shape[1] != 2:
        return
    df.columns = ['X', 'Y']
    res = coef_linea(df)
    SYY = ((df.Y - df.Y.mean()) ** 2).sum()
    # somme des carrés des résidus
    SR = ((df.Y - res[0] - res[1] * df.X) ** 2).sum()
    return 1 - SR / SYY


def poly_deter(df):
    """
    determine le coefficient de determination pour la regression quadratique
    :param df: DataFrame a deux colonnes contenant les donnees a etudier
    :return: le coefficient de determination
    """
    if df.shape[1] != 2:
        return
    df.columns = ['X', 'Y']
    res = coef_poly(df)
    SR = ((df.Y - res[0] - res[1] * df.X - res[2] * df.X ** 2) ** 2).sum()
    SYY = ((df.Y - df.Y.mean()) ** 2).sum()
    return 1 - SR / SYY


BIAS = 1  # Constante pour modifier le taux d'apprentissage
TAILLE_APP = 0.7  # Pourcentage par defaut de la partition d'apprentissage
NBLOOP = 100  # Nombre par defaut d'iteration pour l'apprentissage


class MultiClassPerceptron():
    taux = {}

    def __init__(self, classes, colonnes, donnees, classValue, tailleapp=TAILLE_APP, nbloop=NBLOOP):
        """
        Creation d'un perceptron multiclasse permettant de predire une classe d'un attribut environnemental choisi.
        :param classes: Liste des classes de l'attribut choisi
        :param colonnes: Liste des colonnes du Dataframe
        :param donnees: Dataframe des donnees avec en format records avec la classe associee
        :param classValue: Dictionnaire des classes avec les intervalles associées
        :param tailleapp: Pourcentage par defaut de la partition d'apprentissage.
        :param nbloop: Nombre par defaut d'iteration pour l'apprentissage.
        """
        self.classes = classes
        self.class_value = classValue
        self.colonnes = colonnes
        self.donnees = donnees
        self.nbloop = nbloop

        # Separation des partitions trainpart et testpart
        random.shuffle(self.donnees)
        self.trainpart = self.donnees[:int(len(self.donnees) * tailleapp)]
        self.testpart = self.donnees[int(len(self.donnees) * tailleapp):]

        # Initialisation des vecteurs de poids
        self.vecteur_poids = {c: np.array([0 for _ in range(len(colonnes) + 1)]) for c in self.classes}

    def train(self):
        """
        Entraine le perceptron a partir des donnees fournies a l'inititialisation.
        Boucle pendant le nombre d'iteration choisi, les poids doivent etre stables de preference a la fin de
        l'apprentissage.
        :return: None
        """
        for _ in range(self.nbloop):
            change = False
            for Y, Xb in self.trainpart:
                # Ajoute BIAS a X
                colonnes = [Xb[k] for k in self.colonnes]
                colonnes.append(BIAS)
                X = np.array(colonnes)

                valeur_max = 0
                prediction = self.classes[0]

                for c in self.classes:
                    produit = np.dot(X, self.vecteur_poids[c])
                    if produit >= valeur_max:
                        valeur_max, prediction = produit, c

                if (Y != prediction):
                    change = True
                    np.add(self.vecteur_poids[Y], X, out=self.vecteur_poids[Y], casting="unsafe")
                    np.subtract(self.vecteur_poids[prediction], X, out=self.vecteur_poids[prediction], casting="unsafe")
            if not (change):
                print("Arrêt train : Plus de changement")
                break

    def predict(self, X):
        """
        Predit la classe d'un nouvel individu avec le perceptron entraine.
        :param X: Donnees de l'individu a classer sous forme de dictionnaire (sans la colonne de l'attribut a classer)
        :return: la classe predite de X par le perceptron
        """
        colonnes = [X[k] for k in self.colonnes]
        colonnes.append(BIAS)
        arrayX = np.array(colonnes)

        valeur_max = 0
        prediction = self.classes[0]

        for c in self.classes:
            produit = np.dot(arrayX, self.vecteur_poids[c])
            if produit >= valeur_max:
                valeur_max, prediction = produit, c

        return prediction

    def tauxPrec(self, pr=False):
        """
        Calcule le taux de precision pour chaque classe dans la partition testpart et la precision totale du perceptron

        :param pr: boolean pour afficher les détails sur le taux de précision
        :return: None
        """
        positif = 0
        negatif = 0
        classes = [f[0] for f in self.testpart]
        nbCorrect = {c: 0 for c in classes}
        nbTotal = {c: 0 for c in classes}
        restab = []

        for Xb in self.testpart:
            Y = Xb[0]
            res = self.predict(Xb[1])
            restab.append(res)
            if Y == res:
                nbCorrect[Y] += 1
                nbTotal[Y] += 1
                positif += 1
            else:
                nbTotal[Y] += 1
                negatif += 1

        if pr:
            print("Intervalle des valeurs par classe:\n", self.class_value, "\n")
            print("Valeur de classe a predire:\n", classes, "\n")
            print("Prediction:\n", restab, "\n")
            print("Precision par classe:\n")
        for c in nbCorrect:
            if nbTotal[c] > 0:
                self.taux[c] = (nbCorrect[c] * 1.0) / (nbTotal[c] * 1.0)
            else:
                self.taux[c] = 0
            if pr:
                print("Classe ", c, " : ", self.taux[c])
        res = (positif * 1.0) / ((positif + negatif) * 1.0)
        if pr:
            if positif + negatif != 0:
                print("\nPrecision du perceptron:", res)
            else:
                print("\nIl n'y pas de partition test")
        return res

    def getAttVal(self, categorie):
        """
        Retourne la valeur moyenne d'un intervalle de valeur selon la catégorie d'un attribut.

        :param categorie: la catégorie de l'attribut
        :return: retourne la valeur moyenne de la catégorie en float
        """

        if categorie not in self.class_value:
            print("La categorie n'est pas valide.")
            return
        return self.class_value[categorie].mid


def percMulti(listeData, attribut, nbclasse=20):
    """
    Prepare les donnees a partir des fichiers csv Arduino, pour construire un perceptron Multiclass.
    :param listeData: Dataframe en format Jour, Mois, Heure, Minutes, Secondes, Lieu, Couloir, Temperature, Humidite,
                      Particules, Qualite, Son
    :param attribut: Nom de l'attribut a classer en String
    :param nbclasse: Nombre de classes possibles
    :return: l'objet du perceptron
    """
    # ajout du jour de la semaine
    ld = listeData.copy()
    ld['year'] = 2020
    ld = ld.rename(columns={'Jour': 'day', 'Mois': 'month'})
    ld['datetime'] = pd.to_datetime(ld[['day', 'month', 'year']])
    ld = ld.drop(['year', 'Secondes', 'Minutes'], axis=1)
    ld['weekday'] = ld['datetime'].dt.dayofweek
    ld = ld.drop('datetime', axis=1)
    ld = ld.rename(columns={'day': 'Jour', 'month': 'Mois'})

    # transformation de l'attribut en type Category
    catAtt = "cat" + attribut
    interAtt = "inter" + attribut
    ld[catAtt] = pd.qcut(ld[attribut], nbclasse, labels=False, duplicates='drop')  # without interval
    ld[interAtt] = pd.qcut(ld[attribut], nbclasse, duplicates='drop')

    colonnes = ['Humidite', 'Son', 'Qualite', 'Temperature', 'Particules', 'Jour', 'Mois', 'Couloir', 'Index']
    ld = ld.drop(colonnes, axis=1)
    rec = ld[[catAtt, interAtt]].drop_duplicates().to_dict('records')
    ld = ld.drop(interAtt, axis=1)

    rec = {r[catAtt]: r[interAtt] for r in rec}
    classes = ld[catAtt].unique()
    colonnes = list(ld)[:-1]
    donnees = list(zip(ld[catAtt].tolist(), ld.drop(catAtt, axis=1).to_dict('records')))
    perc = MultiClassPerceptron(classes, colonnes, donnees, rec, nbloop=200)
    perc.train()
    return perc
