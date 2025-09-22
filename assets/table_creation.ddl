
CREATE TABLE "EMPRESA" (
	id INTEGER NOT NULL, 
	nome VARCHAR2(255 CHAR) NOT NULL, 
	cnpj VARCHAR2(14 CHAR), 
	logradouro VARCHAR2(255 CHAR), 
	numero VARCHAR2(255 CHAR), 
	bairro VARCHAR2(255 CHAR), 
	cidade VARCHAR2(255 CHAR), 
	estado VARCHAR(2 CHAR), 
	cep VARCHAR2(8 CHAR), 
	PRIMARY KEY (id), 
	UNIQUE (nome), 
	UNIQUE (cnpj)
)

;


CREATE TABLE "EQUIPAMENTO" (
	id INTEGER NOT NULL, 
	nome VARCHAR2(255 CHAR) NOT NULL, 
	modelo VARCHAR2(255 CHAR), 
	localizacao VARCHAR2(255 CHAR), 
	descricao CLOB, 
	observacoes CLOB, 
	data_instalacao DATE, 
	PRIMARY KEY (id), 
	UNIQUE (nome)
)

;


CREATE TABLE "TIPO_SENSOR" (
	id INTEGER NOT NULL, 
	nome VARCHAR2(255 CHAR) NOT NULL, 
	tipo VARCHAR(15 CHAR) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (nome)
)

;


CREATE TABLE "MANUTENCAO_EQUIPAMENTO" (
	id INTEGER NOT NULL, 
	equipamento_id INTEGER NOT NULL, 
	data_previsao_manutencao DATE, 
	motivo CLOB, 
	data_inicio_manutencao DATE, 
	data_fim_manutencao DATE, 
	descricao CLOB, 
	observacoes CLOB, 
	custo FLOAT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(equipamento_id) REFERENCES "EQUIPAMENTO" (id)
)

;


CREATE TABLE "SENSOR" (
	id INTEGER NOT NULL, 
	tipo_sensor_id INTEGER NOT NULL, 
	nome VARCHAR2(255 CHAR), 
	cod_serial VARCHAR2(255 CHAR), 
	descricao VARCHAR2(255 CHAR), 
	data_instalacao DATE, 
	equipamento_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(tipo_sensor_id) REFERENCES "TIPO_SENSOR" (id), 
	UNIQUE (nome), 
	FOREIGN KEY(equipamento_id) REFERENCES "EQUIPAMENTO" (id)
)

;


CREATE TABLE "LEITURA_SENSOR" (
	id INTEGER NOT NULL, 
	sensor_id INTEGER NOT NULL, 
	data_leitura DATE NOT NULL, 
	valor FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(sensor_id) REFERENCES "SENSOR" (id)
)

;

