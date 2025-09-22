from src.machine_learning.dateset_manipulation import get_dataframe_leituras_sensores
from src.database.tipos_base.database import Database
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import RandomizedSearchCV
import threading
from datetime import datetime
from sklearn.metrics import f1_score
import joblib
import os

RANDOM_STATE = 59

def train_test_split_scaled():
    """
    Realiza o split dos dados em treino e teste, aplicando o MinMaxScaler.
    :return: Tupla com os dados de treino e teste (X_train, X_test, y_train, y_test).
    """

    df = get_dataframe_leituras_sensores()

    features = df.drop(columns=['Manutencao', 'data_leitura'])
    target = df['Manutencao']

    scaler = MinMaxScaler()

    features_scaled = scaler.fit_transform(features)

    return train_test_split(
        features_scaled, target, test_size=0.2, random_state=RANDOM_STATE
    )

def discover_random_forest(X_train, y_train) -> RandomForestClassifier:
    """
    Descobre os melhores hiperparâmetros para o RandomForestClassifier usando GridSearchCV.
    """

    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10]
    }

    clf = RandomForestClassifier(random_state=RANDOM_STATE)
    grid_search = RandomizedSearchCV(clf, param_grid, cv=5, scoring='f1')
    grid_search.fit(X_train, y_train)

    return grid_search.best_estimator_

def discover_logistic_regression(X_train, y_train):
    param_grid = {
        'C': [0.01, 0.1, 1, 10],
        'solver': ['liblinear', 'lbfgs']
    }
    clf = LogisticRegression(random_state=RANDOM_STATE, max_iter=1000)
    search = RandomizedSearchCV(clf, param_grid, cv=5, scoring='f1')
    search.fit(X_train, y_train)
    return search.best_estimator_

def discover_svc(X_train, y_train):
    param_grid = {
        'C': [0.1, 1, 10],
        'kernel': ['linear', 'rbf'],
        'gamma': ['scale', 'auto']
    }
    clf = SVC(random_state=RANDOM_STATE)
    search = RandomizedSearchCV(clf, param_grid, cv=5, scoring='f1')
    search.fit(X_train, y_train)
    return search.best_estimator_

# KNeighborsClassifier
def discover_kneighbors(X_train, y_train):
    param_grid = {
        'n_neighbors': [3, 5, 7, 9],
        'weights': ['uniform', 'distance']
    }
    clf = KNeighborsClassifier()
    search = RandomizedSearchCV(clf, param_grid, cv=5, scoring='f1')
    search.fit(X_train, y_train)
    return search.best_estimator_

def discover_gradient_boosting(X_train, y_train):
    param_grid = {
        'n_estimators': [50, 100, 200],
        'learning_rate': [0.01, 0.1, 0.2],
        'max_depth': [3, 5, 7]
    }
    clf = GradientBoostingClassifier(random_state=RANDOM_STATE)
    search = RandomizedSearchCV(clf, param_grid, cv=5, scoring='f1')
    search.fit(X_train, y_train)
    return search.best_estimator_

def train_all_models_multi_thread() -> dict:
    """ Treina todos os modelos em threads separadas.
    :returns dicionário com os modelos treinados. Ex: {'random_forest': model_rf, 'logistic_regression': model_lr, ...}
    """

    before = datetime.now()
    print(f"[{before.strftime('%Y-%m-%d %H:%M:%S')}] Starting training all models...")

    X_train, X_test, y_train, y_test = train_test_split_scaled()

    def _train_in_thread(target_func, X_train, y_train, results, key):

        before = datetime.now()

        print(f"[{before.strftime('%Y-%m-%d %H:%M:%S')}] Starting training for {key}")
        results[key] = target_func(X_train, y_train)
        now = datetime.now()
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Finished training for {key} in {now - before}")

    results = {}
    threads = []
    functions = {
        'random_forest': discover_random_forest,
        'logistic_regression': discover_logistic_regression,
        'svc': discover_svc,
        'kneighbors': discover_kneighbors,
        'gradient_boosting': discover_gradient_boosting
    }

    for key, func in functions.items():
        thread = threading.Thread(target=_train_in_thread, args=(func, X_train, y_train, results, key))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print(f"[{before.strftime('%Y-%m-%d %H:%M:%S')}] Finished training all models.")

    return results

def salvar_modelos(resultados, pasta_destino='modelos_salvos'):
    os.makedirs(pasta_destino, exist_ok=True)
    for nome, modelo in resultados.items():
        caminho = os.path.join(pasta_destino, f'{nome}.joblib')
        joblib.dump(modelo, caminho)
        print(f'Modelo {nome} salvo em {caminho}')


if __name__ == '__main__':

    pd.set_option('display.max_columns', 50)

    Database.init_sqlite(r'C:\Users\Lucas\PycharmProjects\fiap_sprint3_reply_leo\database.db')
    Database.create_all_tables()

    resultados = train_all_models_multi_thread()

    X_train, X_test, y_train, y_test = train_test_split_scaled()

    for nome, modelo in resultados.items():
        y_pred = modelo.predict(X_test)
        f1 = f1_score(y_test, y_pred)
        print(f"{nome}: F1-score = {f1:.4f}")

    salvar_modelos(resultados)