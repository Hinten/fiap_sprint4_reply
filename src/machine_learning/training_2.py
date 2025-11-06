"""
Treinamento de um modelo RNN (LSTM) usando o MESMO dataset utilizado pelos modelos clássicos
em `training.py`, isto é, o DataFrame retornado por
`src.machine_learning.dateset_manipulation.get_dataframe_leituras_sensores`.

Contrato rápido:
- Entrada: DataFrame com colunas [data_leitura, <features por tipo_sensor...>, Manutencao]
- Pré-processamento: ordenar por data, escalar features com MinMaxScaler
- Janela temporal: window_size passos (padrão 20) para prever Manutencao do passo seguinte
- Saída: modelo Keras salvo em `modelos_salvos/modelo_rnn.keras` + scaler em `modelos_salvos/scaler_rnn.joblib`
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Tuple

import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score, classification_report
import joblib

from src.machine_learning.dateset_manipulation import get_dataframe_leituras_sensores
from src.database.tipos_base.database import Database

# Força execução em CPU (desabilita GPU) antes de importar TensorFlow
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# TensorFlow / Keras
try:
	import tensorflow as tf
	from tensorflow.keras import Sequential
	from tensorflow.keras.layers import Input, LSTM, Dense, Dropout, Conv1D
	from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
	# Tentativa adicional para garantir que nenhuma GPU seja usada
	try:
		tf.config.set_visible_devices([], 'GPU')
	except Exception:
		pass
except Exception as e:  # pragma: no cover - ambiente pode não ter TF instalado ainda
	raise RuntimeError(
		"TensorFlow/Keras não está instalado. Adicione 'tensorflow' ao requirements e instale as dependências."
	) from e


RANDOM_STATE = 59


@dataclass
class RNNTrainingConfig:
	window_size: int = 20
	test_size: float = 0.2  # split temporal (última fração vira teste)
	epochs: int = 50
	batch_size: int = 32
	model_dir: str = "machine_learning/modelos_salvos"
	model_name: str = "modelo_rnn.keras"
	scaler_name: str = "scaler_rnn.joblib"


def _build_sequences(X: np.ndarray, y: np.ndarray, window_size: int) -> Tuple[np.ndarray, np.ndarray]:
	"""
	Constrói janelas temporais para RNN.
	X shape (N, F) -> X_seq shape (N - ws, ws, F)
	y shape (N,)   -> y_seq shape (N - ws,)
	"""
	if len(X) != len(y):
		raise ValueError("X e y devem ter o mesmo comprimento")
	if len(X) <= window_size:
		raise ValueError(f"Dataset muito curto para window_size={window_size} (N={len(X)})")

	X_seq = []
	y_seq = []
	for i in range(window_size, len(X)):
		X_seq.append(X[i - window_size:i])
		y_seq.append(y[i])
	return np.asarray(X_seq, dtype=np.float32), np.asarray(y_seq, dtype=np.float32)


def _time_series_split(X_seq: np.ndarray, y_seq: np.ndarray, test_size: float) -> Tuple[np.ndarray, ...]:
	"""
	Split temporal simples: primeiras (1-test)% para treino, últimas test% para teste.
	"""
	n = len(X_seq)
	if n < 2:
		raise ValueError("Poucos exemplos após criação de sequências.")
	split_idx = int(n * (1 - test_size))
	if split_idx <= 0 or split_idx >= n:
		raise ValueError("Parâmetro test_size gerou split inválido.")
	return X_seq[:split_idx], X_seq[split_idx:], y_seq[:split_idx], y_seq[split_idx:]


def _build_model(input_timesteps: int, n_features: int) -> Sequential:
	model = Sequential([
		Input(shape=(input_timesteps, n_features)),
		LSTM(64, return_sequences=False),
		Conv1D(32, kernel_size=3, activation="relu"),
		Dropout(0.2),
		Dense(32, activation="relu"),
		Dense(1, activation="sigmoid"),  # binário
	])
	model.compile(
		optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
		loss="binary_crossentropy",
		metrics=["accuracy"],
	)
	return model


def train_rnn_model(cfg: RNNTrainingConfig = RNNTrainingConfig()) -> dict:
	# 1) Carrega dataset e ordena por tempo
	df = get_dataframe_leituras_sensores()
	if "data_leitura" not in df.columns or "Manutencao" not in df.columns:
		raise ValueError("DataFrame precisa conter 'data_leitura' e 'Manutencao'.")

	df = df.sort_values("data_leitura").reset_index(drop=True)

	# 2) Separa features e alvo
	feature_cols = [c for c in df.columns if c not in ("data_leitura", "Manutencao")]
	if len(feature_cols) == 0:
		raise ValueError("Nenhuma feature encontrada após remover 'data_leitura' e 'Manutencao'.")

	X_raw = df[feature_cols].to_numpy(dtype=np.float32)
	y_raw = df["Manutencao"].astype(np.float32).to_numpy()

	# 3) Escalonamento (fit só no conjunto de treino para evitar vazamento)
	# Para isso, primeiro criamos as sequências completas e depois split temporal; porém o scaler deve
	# ser ajustado APENAS no período de treino original (antes de janelar). Uma forma simples:
	# - Determinar índice de split no espaço "por linha", não por sequência
	n_total = len(df)
	split_idx_rows = int(n_total * (1 - cfg.test_size))
	if split_idx_rows <= cfg.window_size:
		raise ValueError("Dataset insuficiente para split+janela. Reduza window_size ou colete mais dados.")

	scaler = MinMaxScaler()
	X_train_rows = X_raw[:split_idx_rows]
	scaler.fit(X_train_rows)
	X_scaled = scaler.transform(X_raw)

	# 4) Sequências
	X_seq, y_seq = _build_sequences(X_scaled, y_raw, cfg.window_size)

	# 5) Split temporal em nível de sequência
	X_train, X_test, y_train, y_test = _time_series_split(X_seq, y_seq, cfg.test_size)

	# 6) Modelo
	model = _build_model(cfg.window_size, X_train.shape[-1])

	# 7) Treinamento com callbacks
	os.makedirs(cfg.model_dir, exist_ok=True)
	model_path = os.path.join(cfg.model_dir, cfg.model_name)
	callbacks = [
		EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
		ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-6),
		ModelCheckpoint(model_path, monitor="val_loss", save_best_only=True),
	]

	history = model.fit(
		X_train,
		y_train,
		validation_split=0.2,
		epochs=cfg.epochs,
		batch_size=cfg.batch_size,
		callbacks=callbacks,
		verbose=2,
	)

	# 8) Avaliação
	y_proba = model.predict(X_test, verbose=0).ravel()
	y_pred = (y_proba >= 0.5).astype(int)

	metrics = {
		"accuracy": float(accuracy_score(y_test, y_pred)),
		"f1": float(f1_score(y_test, y_pred, zero_division=0)),
		"roc_auc": float(roc_auc_score(y_test, y_proba)) if len(np.unique(y_test)) > 1 else float("nan"),
		"classification_report": classification_report(y_test, y_pred, zero_division=0),
		"model_path": model_path,
	}

	# 9) Persistência
	scaler_path = os.path.join(cfg.model_dir, cfg.scaler_name)
	joblib.dump(scaler, scaler_path)
	metrics["scaler_path"] = scaler_path

	return metrics


if __name__ == "__main__":
	# Inicializa SQLite por padrão (usa ./database.db). Altere se necessário.
	try:
		Database.init_sqlite()
		# Se necessário, crie tabelas. Não gera dados automaticamente.
		Database.create_all_tables()
	except Exception:
		# Se a aplicação já inicializa em outro ponto, ignore falhas aqui.
		pass

	cfg = RNNTrainingConfig()
	print("Iniciando treino RNN com config:", cfg)
	try:
		result = train_rnn_model(cfg)
		print("\n== Métricas RNN ==")
		for k, v in result.items():
			if k != "classification_report":
				print(f"{k}: {v}")
		print("\nRelatório:\n", result["classification_report"]) 
		print(f"\nModelo salvo em: {result['model_path']}")
		print(f"Scaler salvo em: {result['scaler_path']}")
	except Exception as e:
		print("Erro durante o treinamento RNN:", e)

